
import api from '../services/api';

const DB_NAME = 'BiliDMJ_Cache';
const DB_VERSION = 1;
const STORE_NAME = 'avatars';

class AvatarCacheManager {
    constructor() {
        this.db = null;
        this.initPromise = this.initDB();
        this.memoryCache = new Map(); // url -> objectUrl
        this.pendingRequests = new Map(); // url -> Promise
    }

    async initDB() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = (event) => {
                console.error('IndexedDB error:', event.target.error);
                reject(event.target.error);
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    const objectStore = db.createObjectStore(STORE_NAME, { keyPath: 'url' });
                    objectStore.createIndex('lastAccessed', 'lastAccessed', { unique: false });
                    objectStore.createIndex('type', 'type', { unique: false });
                }
            };
        });
    }

    async get(url) {
        if (!url) return null;
        
        // 1. Check memory cache
        if (this.memoryCache.has(url)) {
            return this.memoryCache.get(url);
        }

        await this.initPromise;

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readonly');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.get(url);

            request.onsuccess = (event) => {
                const result = event.target.result;
                if (result) {
                    // Update lastAccessed asynchronously
                    this.updateLastAccessed(result);
                    
                    const objectUrl = URL.createObjectURL(result.blob);
                    this.memoryCache.set(url, objectUrl);
                    resolve(objectUrl);
                } else {
                    resolve(null);
                }
            };

            request.onerror = () => reject(request.error);
        });
    }

    updateLastAccessed(record) {
        const transaction = this.db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        record.lastAccessed = Date.now();
        store.put(record);
    }

    async save(url, blob, type = 'avatar') {
        await this.initPromise;
        
        // If type is qrcode, delete old qrcodes first
        if (type === 'qrcode') {
            await this.deleteByType('qrcode');
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            
            const record = {
                url,
                blob,
                type,
                timestamp: Date.now(),
                lastAccessed: Date.now()
            };

            const request = store.put(record);

            request.onsuccess = () => {
                // Also update memory cache
                const objectUrl = URL.createObjectURL(blob);
                this.memoryCache.set(url, objectUrl);
                
                // Trigger cleanup if needed (e.g., limit check)
                // We do this lazily/async to not block
                this.checkQuota();
                
                resolve(objectUrl);
            };
            
            request.onerror = () => reject(request.error);
        });
    }

    async deleteByType(type) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            const index = store.index('type');
            const request = index.getAllKeys(type);

            request.onsuccess = (event) => {
                const keys = event.target.result;
                if (keys && keys.length > 0) {
                    keys.forEach(key => {
                        store.delete(key);
                        // Also clear from memory cache
                        if (this.memoryCache.has(key)) {
                            URL.revokeObjectURL(this.memoryCache.get(key));
                            this.memoryCache.delete(key);
                        }
                    });
                }
                resolve();
            };
            request.onerror = () => reject(request.error);
        });
    }
    
    async checkQuota() {
        // Simple quota check: keep max 1000 items
        const MAX_ITEMS = 1000;
        
        const transaction = this.db.transaction([STORE_NAME], 'readonly');
        const store = transaction.objectStore(STORE_NAME);
        const countRequest = store.count();
        
        countRequest.onsuccess = () => {
            if (countRequest.result > MAX_ITEMS) {
                this.pruneOldest(countRequest.result - MAX_ITEMS + 50); // Remove excess + buffer
            }
        };
    }
    
    async pruneOldest(count) {
        const transaction = this.db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        const index = store.index('lastAccessed');
        const request = index.openCursor(); // Ascending order (oldest first)
        
        let deleted = 0;
        request.onsuccess = (event) => {
            const cursor = event.target.result;
            if (cursor && deleted < count) {
                store.delete(cursor.primaryKey);
                // Clear from memory cache
                if (this.memoryCache.has(cursor.primaryKey)) {
                    URL.revokeObjectURL(this.memoryCache.get(cursor.primaryKey));
                    this.memoryCache.delete(cursor.primaryKey);
                }
                deleted++;
                cursor.continue();
            }
        };
    }

    async cleanupExpired() {
        const MAX_AGE = 7 * 24 * 60 * 60 * 1000; // 7 days
        const threshold = Date.now() - MAX_AGE;

        const transaction = this.db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        // We need an index on timestamp if we want to be efficient, or just iterate all.
        // I added timestamp index in initDB.
        const index = store.index('timestamp');
        const range = IDBKeyRange.upperBound(threshold);
        const request = index.openCursor(range);

        request.onsuccess = (event) => {
            const cursor = event.target.result;
            if (cursor) {
                store.delete(cursor.primaryKey);
                if (this.memoryCache.has(cursor.primaryKey)) {
                    URL.revokeObjectURL(this.memoryCache.get(cursor.primaryKey));
                    this.memoryCache.delete(cursor.primaryKey);
                }
                cursor.continue();
            }
        };
    }

    async clearAll() {
        await this.initPromise;
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.clear();
            
            request.onsuccess = () => {
                // Clear memory cache
                this.memoryCache.forEach(url => URL.revokeObjectURL(url));
                this.memoryCache.clear();
                resolve(true);
            };
            
            request.onerror = () => reject(request.error);
        });
    }
    
    // Fetch and cache wrapper
    async loadImage(url, type = 'avatar') {
        if (!url) return null;

        // Check if pending
        if (this.pendingRequests.has(url)) {
            return this.pendingRequests.get(url);
        }

        const promise = (async () => {
            try {
                // 1. Try get from cache
                const cachedUrl = await this.get(url);
                if (cachedUrl) return cachedUrl;

                // 2. Fetch from proxy or direct
                // Construct proxy URL only for external Bilibili images
                let fetchUrl = url;
                if (url.includes('hdslb.com') || url.includes('bilibili.com')) {
                    fetchUrl = `${api.defaults.baseURL}/proxy/image?url=${encodeURIComponent(url)}`;
                }
                
                const response = await fetch(fetchUrl);
                if (!response.ok) throw new Error('Network response was not ok');
                
                const blob = await response.blob();
                
                // 3. Save to cache
                return await this.save(url, blob, type);
            } catch (error) {
                console.error('Failed to load image:', url, error);
                // On error, try returning direct proxy URL as fallback (though it might fail if 403, but worth a shot or just null)
                // Actually if fetch failed, the direct usage in img tag will also fail. 
                // Return null or let the component handle error.
                return null;
            } finally {
                this.pendingRequests.delete(url);
            }
        })();

        this.pendingRequests.set(url, promise);
        return promise;
    }
}

export const avatarCache = new AvatarCacheManager();
