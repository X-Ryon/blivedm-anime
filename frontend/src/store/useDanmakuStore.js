import { create } from 'zustand';
import { danmakuApi } from '../services/api';

const formatTime = (timestamp) => {
    // timestamp is in seconds (float/int)
    // If timestamp is 0 or null/undefined, use current time
    const date = (timestamp && timestamp > 0) ? new Date(timestamp * 1000) : new Date();
    const Y = date.getFullYear();
    const M = (date.getMonth() + 1).toString().padStart(2, '0');
    const D = date.getDate().toString().padStart(2, '0');
    const h = date.getHours().toString().padStart(2, '0');
    const m = date.getMinutes().toString().padStart(2, '0');
    const s = date.getSeconds().toString().padStart(2, '0');
    return `${Y}-${M}-${D} ${h}:${m}:${s}`;
};

const useDanmakuStore = create((set) => ({
    // Connection State
    isConnected: false,
    roomId: null,
    roomTitle: "-",
    anchorName: "-",
    
    // Data Lists
    danmakuList: [],
    giftList: [], // Includes gifts and guards
    scList: [],
    totalRevenue: 0,
    
    // UI State
    searchText: '',
    
    // Actions
    setConnected: (isConnected, roomId) => set({ isConnected, roomId }),
    setRoomTitle: (roomTitle) => set({ roomTitle }),
    setAnchorName: (anchorName) => set({ anchorName }),
    setSearchText: (searchText) => set({ searchText }),
    
    addDanmaku: (danmaku) => set((state) => {
        // Add unique ID if missing (backend might not provide unique ID for every msg)
        const newItem = {
            ...danmaku,
            id: danmaku.id || Date.now() + Math.random(),
            // Map backend fields to frontend expected fields if necessary
            // Backend: user_name, dm_text, face_img, level, privilege_name, identity
            // Frontend DanmakuItem: username, content, avatar, level, guardLevel (derived)
            username: danmaku.user_name,
            content: danmaku.dm_text,
            avatar: danmaku.face_img || '',
            // guardLevel mapping: "舰长"->3, "提督"->2, "总督"->1
            guardLevel: danmaku.privilege_name === "舰长" ? 3 : 
                       danmaku.privilege_name === "提督" ? 2 : 
                       danmaku.privilege_name === "总督" ? 1 : 0
        };
        return { danmakuList: [...state.danmakuList, newItem].slice(-200) };
    }),
    
    addGift: (gift) => set((state) => {
        console.log('addGift called with:', gift);
        console.log('Current totalRevenue:', state.totalRevenue);
        const price = Number(gift.price) || 0;
        console.log('Adding price:', price);
        
        const newItem = {
            ...gift,
            id: gift.id || Date.now() + Math.random(),
            // Frontend GiftItem: username, giftName, count, price, avatar, level, time
            username: gift.user_name,
            giftName: gift.gift_type, // Backend sends gift_type
            count: gift.num,
            price: gift.price,
            // avatar: gift.face_img || '', // Removed face_img
            giftImg: gift.gift_img || '', // Add giftImg
            level: gift.level,
            time: formatTime(gift.timestamp)
        };
        const newTotal = state.totalRevenue + price;
        console.log('New totalRevenue:', newTotal);
        
        return { 
            giftList: [...state.giftList, newItem].slice(-200),
            totalRevenue: newTotal
        };
    }),
    
    addSc: (sc) => set((state) => {
        console.log('addSc called with:', sc);
        
        const price = Number(sc.price) || 0;
        
        const newItem = {
            ...sc,
            id: sc.id || Date.now() + Math.random(),
            // Frontend ScItem: username, content, price, avatar, time
            username: sc.user_name,
            content: sc.dm_text, // Backend sends dm_text for SC content
            price: sc.price,
            // avatar: sc.face_img || '', // Removed face_img
            time: formatTime(sc.timestamp)
        };
        return { 
            scList: [...state.scList, newItem].slice(-100),
            totalRevenue: state.totalRevenue + price
        };
    }),

    // Gift Metadata
    giftMetadata: {},
    updateGiftMetadata: (giftList) => {
        const map = {};
        if (Array.isArray(giftList)) {
            giftList.forEach(gift => {
                if (gift.name && gift.img) {
                    map[gift.name] = gift.img;
                }
            });
        }
        set({ giftMetadata: map });
    },

    clearAll: () => set({ 
        danmakuList: [], 
        giftList: [], 
        scList: [],
        totalRevenue: 0
    }),

    fetchHistory: async (roomId) => {
        try {
            const [danmakuRes, giftRes, scRes] = await Promise.all([
                danmakuApi.getDanmakuHistory(roomId),
                danmakuApi.getGiftHistory(roomId),
                danmakuApi.getScHistory(roomId)
            ]);

            if (danmakuRes.code === 200) {
                 const danmakuList = danmakuRes.data.map(d => ({
                     ...d,
                     id: d.uid + '_' + Math.random(), // Use simple unique ID
                     username: d.user_name,
                     content: d.dm_text,
                     avatar: d.face_img,
                     guardLevel: d.privilege_name === "舰长" ? 3 : 
                                d.privilege_name === "提督" ? 2 : 
                                d.privilege_name === "总督" ? 1 : 0
                 }));
                 set(state => ({ danmakuList: [...danmakuList, ...state.danmakuList].slice(-5000) }));
             }
            
             if (giftRes.code === 200) {
                 const giftList = giftRes.data.map(g => ({
                     ...g,
                     id: g.uid + '_' + Math.random(),
                     username: g.user_name,
                     giftName: g.gift_type,
                     count: g.num,
                     price: g.price,
                     // avatar: g.face_img || '',
                     level: g.level,
                     time: formatTime(g.timestamp)
                 }));
                 set(state => ({ giftList: [...giftList, ...state.giftList].slice(-2000) }));
             }

             if (scRes.code === 200) {
                  const scList = scRes.data.map(s => ({
                     ...s,
                     id: s.uid + '_' + Math.random(),
                     username: s.user_name,
                     content: s.dm_text,
                     price: s.price,
                     // avatar: s.face_img,
                     time: formatTime(s.timestamp)
                 }));
                 set(state => ({ scList: [...scList, ...state.scList].slice(-1000) }));
             }
        } catch (error) {
            console.error("Failed to fetch history:", error);
        }
    }
}));


export default useDanmakuStore;
