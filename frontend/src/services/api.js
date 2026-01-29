import axios from 'axios';

// 配置 axios 实例
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1', // 假设后端运行在 8000 端口
    timeout: 10000,
});

// 响应拦截器处理错误
api.interceptors.response.use(
    response => response.data,
    error => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

export const authApi = {
    // 获取登录二维码
    getQrcode: () => api.get('/auth/qrcode'),
    
    // 轮询登录状态
    pollLoginStatus: (qrcodeKey) => api.get('/auth/poll', { params: { qrcode_key: qrcodeKey } }),
    
    // 根据 UID 获取用户信息
    getUserByUid: (uid) => api.get(`/auth/user/${uid}`),

    // 获取所有保存的用户列表
    getUsersList: () => api.get('/users/list'),

    // 删除指定用户
    deleteUser: (uid) => api.delete(`/users/${uid}`),
};

export const giftApi = {
    // 获取礼物列表
    getGiftList: () => api.get('/gift/list'),
};

export const resourceApi = {
    // 获取素材列表
    getAssets: () => api.get('/resources/assets'),
};

export const systemApi = {
    // 获取系统配置
    getConfig: () => api.get('/config'),
    // 更新系统配置
    updateConfig: (config) => api.post('/config', config),
    // 重置系统配置
    resetConfig: () => api.post('/config/reset'),
};

export const listenerApi = {
    start: (roomId, sessdata) => api.post('/listener/start', { room_id: roomId, sessdata: sessdata }),
    stop: () => api.post('/listener/stop'),
};

export const danmakuApi = {
    getDanmakuHistory: (roomId, limit = 100) => api.get('/danmaku/history/danmaku', { params: { room_id: roomId, limit } }),
    getGiftHistory: (roomId, limit = 100) => api.get('/danmaku/history/gift', { params: { room_id: roomId, limit } }),
    getScHistory: (roomId, limit = 100) => api.get('/danmaku/history/sc', { params: { room_id: roomId, limit } }),
};

export default api;
