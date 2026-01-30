import { create } from 'zustand';
import { authApi, systemApi } from '../services/api';

const useUserStore = create((set, get) => ({
    // 状态
    isLoggedIn: false,
    userInfo: null, // { uid, user_name, face_img }
    sessdata: '',
    config: null,
    
    // Actions
    setLogin: (userInfo, sessdata) => set({ 
        isLoggedIn: true, 
        userInfo, 
        sessdata 
    }),
    
    logout: () => {
        set({ isLoggedIn: false, userInfo: null, sessdata: '' });
        
        // Disable auto_login on logout
        const currentConfig = get().config;
        if (currentConfig && currentConfig.system.auto_login) {
            const newConfig = {
                ...currentConfig,
                system: {
                    ...currentConfig.system,
                    auto_login: false
                }
            };
            get().updateConfig(newConfig);
        }
    },
    
    setConfig: (config) => set({ config }),
    
    // 异步 Actions
    fetchConfig: async () => {
        try {
            const res = await systemApi.getConfig();
            if (res.code === 200) {
                const config = res.data;
                set({ config });
                
                // 自动登录逻辑
                if (config.system.auto_login && config.system.last_uid) {
                    await get().autoLogin(config.system.last_uid);
                }
            }
        } catch (error) {
            console.error('Failed to fetch config:', error);
        } finally {
            set({ isInitialized: true });
        }
    },
    
    updateConfig: async (newConfig) => {
        try {
            const res = await systemApi.updateConfig(newConfig);
            if (res.code === 200) {
                set({ config: res.data });
            }
        } catch (error) {
            console.error('Failed to update config:', error);
        }
    },

    resetConfig: async () => {
        try {
            const res = await systemApi.resetConfig();
            if (res.code === 200) {
                set({ config: res.data });
                return true;
            }
            return false;
        } catch (error) {
            console.error('Failed to reset config:', error);
            return false;
        }
    },
    
    autoLogin: async (uid) => {
        try {
            const res = await authApi.getUserByUid(uid);
            if (res.code === 200) {
                const { sessdata, ...userInfo } = res.data;
                set({ 
                    isLoggedIn: true, 
                    userInfo, 
                    sessdata 
                });
            }
        } catch (error) {
            console.error('Auto login failed:', error);
            // 自动登录失败，可能需要更新配置关闭自动登录？或者只是保持未登录状态
        }
    },
    
    // 登录成功后的处理：保存配置
    handleLoginSuccess: async (userInfo, sessdata) => {
        set({ 
            isLoggedIn: true, 
            userInfo, 
            sessdata 
        });
        
        // 更新配置中的 last_uid (保持 auto_login 不变)
        const currentConfig = get().config;
        if (currentConfig) {
            const newConfig = {
                ...currentConfig,
                system: {
                    ...currentConfig.system,
                    last_uid: userInfo.uid.toString()
                }
            };
            await get().updateConfig(newConfig);
        }
    }
}));

export default useUserStore;
