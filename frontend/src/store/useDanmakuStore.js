import { create } from 'zustand';
import { danmakuApi } from '../services/api';

const useDanmakuStore = create((set) => ({
    // Connection State
    isConnected: false,
    roomId: null,
    roomTitle: "-",
    
    // Data Lists
    danmakuList: [],
    giftList: [], // Includes gifts and guards
    scList: [],
    
    // Actions
    setConnected: (isConnected, roomId) => set({ isConnected, roomId }),
    setRoomTitle: (roomTitle) => set({ roomTitle }),
    
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
            avatar: danmaku.face_img,
            // guardLevel mapping: "舰长"->3, "提督"->2, "总督"->1
            guardLevel: danmaku.privilege_name === "舰长" ? 3 : 
                       danmaku.privilege_name === "提督" ? 2 : 
                       danmaku.privilege_name === "总督" ? 1 : 0
        };
        return { danmakuList: [...state.danmakuList, newItem].slice(-200) };
    }),
    
    addGift: (gift) => set((state) => {
        const newItem = {
            ...gift,
            id: gift.id || Date.now() + Math.random(),
            // Frontend GiftItem: username, giftName, count, price, avatar, level, time
            username: gift.user_name,
            giftName: gift.gift_type, // Backend sends gift_type
            count: gift.num,
            price: gift.price,
            avatar: gift.face_img || '', // Backend might not send face_img for all gifts? check schema
            level: gift.level,
            time: new Date().toLocaleTimeString()
        };
        return { giftList: [...state.giftList, newItem].slice(-200) };
    }),
    
    addSc: (sc) => set((state) => {
        const newItem = {
            ...sc,
            id: sc.id || Date.now() + Math.random(),
            // Frontend ScItem: username, content, price, avatar, time
            username: sc.user_name,
            content: sc.dm_text, // Backend sends dm_text for SC content
            price: sc.price,
            avatar: sc.face_img,
            time: new Date().toLocaleTimeString()
        };
        return { scList: [...state.scList, newItem].slice(-100) };
    }),

    clearAll: () => set({ 
        danmakuList: [], 
        giftList: [], 
        scList: [] 
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
                 set(state => ({ danmakuList: [...danmakuList, ...state.danmakuList].slice(-200) }));
             }
            
             if (giftRes.code === 200) {
                 const giftList = giftRes.data.map(g => ({
                     ...g,
                     id: g.uid + '_' + Math.random(),
                     username: g.user_name,
                     giftName: g.gift_type,
                     count: g.num,
                     price: g.price,
                     avatar: g.face_img || '',
                     level: g.level,
                     time: new Date().toLocaleTimeString() // Fallback time
                 }));
                 set(state => ({ giftList: [...giftList, ...state.giftList].slice(-200) }));
             }

             if (scRes.code === 200) {
                  const scList = scRes.data.map(s => ({
                     ...s,
                     id: s.uid + '_' + Math.random(),
                     username: s.user_name,
                     content: s.dm_text,
                     price: s.price,
                     avatar: s.face_img,
                     time: new Date().toLocaleTimeString()
                 }));
                 set(state => ({ scList: [...scList, ...state.scList].slice(-100) }));
             }
        } catch (error) {
            console.error("Failed to fetch history:", error);
        }
    }
}));


export default useDanmakuStore;
