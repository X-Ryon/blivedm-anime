import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, Space, Card, message } from 'antd';
import { ApiOutlined, KeyOutlined, DisconnectOutlined } from '@ant-design/icons';
import useUserStore from '../../store/useUserStore';
import useDanmakuStore from '../../store/useDanmakuStore';
import { listenerApi } from '../../services/api';

const ConnectionManager = () => {
  const { sessdata, config, updateConfig } = useUserStore();
  const { isConnected, setConnected, addDanmaku, addGift, addSc, clearAll, setRoomTitle, fetchHistory } = useDanmakuStore();
  const [roomId, setRoomId] = useState('');
  const [sessDataInput, setSessDataInput] = useState('');
  const [loading, setLoading] = useState(false);
  const wsRef = useRef(null);

  // 追踪 props/store 的变化，实现类似 getDerivedStateFromProps 的效果
  // 当 store 中的 sessdata 更新时，更新本地 input 和 prev 值
  const [prevSessdata, setPrevSessdata] = useState(sessdata);
  if (sessdata !== prevSessdata) {
    setPrevSessdata(sessdata);
    setSessDataInput(sessdata || '');
  }

  // 当 config 加载后，更新本地 input 和 prev 值
  const configRoomId = config?.system?.last_room_id;
  const [prevConfigRoomId, setPrevConfigRoomId] = useState(configRoomId);
  if (configRoomId !== prevConfigRoomId) {
    setPrevConfigRoomId(configRoomId);
    setRoomId(configRoomId || '');
  }

  const handleConnect = async (targetRoomId, targetSessdata) => {
    // Priority: Argument > State
    const finalRoomId = targetRoomId || roomId;
    // explicit check for undefined because targetSessdata could be empty string
    const finalSessdata = targetSessdata !== undefined ? targetSessdata : sessDataInput;

    if (!finalRoomId) {
        message.error('请输入直播间 Room ID');
        return;
    }

    setLoading(true);
    clearAll(); // 连接新房间前清空旧数据
    try {
        // 1. 调用后端 Start 接口，确保监听任务启动，并传入 Sessdata
        // 如果用户修改了输入框中的 Sessdata，优先使用输入框的值
        // 否则使用 userStore 中的 sessdata
        // user_name 参数已移除，后端不再需要
        const response = await listenerApi.start(finalRoomId, finalSessdata);

        // Update Room Title from response
        if (response && response.room_title) {
            setRoomTitle(response.room_title);
        } else {
            setRoomTitle(`Room ${finalRoomId}`);
        }

        // Fetch History
        fetchHistory(finalRoomId);

        // 2. 建立 WebSocket 连接
        const _wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // 假设后端在 8000 端口，如果前后端同源则不需要硬编码
        const wsUrl = `ws://localhost:8000/api/v1/listener/ws/${finalRoomId}`;
        
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket Connected');
            setConnected(true, finalRoomId);
            setLoading(false);
            message.success(`已连接到房间 ${finalRoomId}`);

            // Update last_room_id in config
            const currentConfig = useUserStore.getState().config;
            if (currentConfig && currentConfig.system && currentConfig.system.last_room_id !== finalRoomId) {
                updateConfig({
                    ...currentConfig,
                    system: {
                        ...currentConfig.system,
                        last_room_id: finalRoomId
                    }
                });
            }
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // 根据 msg_type 分发到不同的 store action
                switch (data.msg_type) {
                    case 'danmaku':
                        addDanmaku(data);
                        break;
                    case 'gift':
                    case 'guard':
                        addGift(data);
                        break;
                    case 'super_chat':
                        addSc(data);
                        break;
                    default:
                        console.log('Unknown message type:', data);
                }
            } catch (e) {
                console.error('Failed to parse message:', e);
            }
        };

        ws.onclose = () => {
            console.log('WebSocket Disconnected');
            setConnected(false, null);
            setLoading(false);
            // message.info('连接已断开');
        };

        ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
            setLoading(false);
            message.error('连接发生错误');
        };

        wsRef.current = ws;

    } catch (error) {
        console.error('Connection failed:', error);
        message.error(`连接失败: ${error.response?.data?.message || error.message}`);
        setLoading(false);
        // 如果后端已启动监听但前端失败，尝试停止监听以重置状态
        try {
            await listenerApi.stop();
        } catch (stopError) {
            console.error('Failed to cleanup listener:', stopError);
        }
    }
  };

  // Auto-connect effect
  const autoConnectAttempted = useRef(false);
  
  // Use a ref to keep handleConnect stable if we don't want to add it to dependencies,
  // OR just disable the rule for handleConnect if it's not memoized.
  // Since handleConnect is defined inside the component and depends on many things,
  // let's suppress the warning for handleConnect, but include sessdata.
  useEffect(() => {
    // Only proceed if config is loaded and we haven't tried yet
    if (config?.system?.auto_connect && config?.system?.last_room_id && !isConnected && !autoConnectAttempted.current) {
        autoConnectAttempted.current = true;
        // Small delay to ensure other states (like sessdata from auto-login) might be ready
        // But to be responsive, we just go.
        console.log('Auto connecting to room:', config.system.last_room_id);
        
        // Use setTimeout to avoid synchronous setState warning and allow other updates to settle
        setTimeout(() => {
            handleConnect(config.system.last_room_id, sessdata);
        }, 0);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [config, isConnected, sessdata]);

  const handleDisconnect = async () => {
      if (wsRef.current) {
          wsRef.current.close();
          wsRef.current = null;
      }
      try {
          await listenerApi.stop();
      } catch (e) {
          console.error('Stop listen failed:', e);
      }
      setConnected(false, null);
      setRoomTitle("-");
      message.success('已断开连接');
  };

  // 组件卸载时断开连接
  useEffect(() => {
      return () => {
          if (wsRef.current) {
              wsRef.current.close();
          }
      };
  }, []);

  return (
    <Card bordered={false} bodyStyle={{ padding: '12px 24px', background: '#f5f5f5', borderRadius: 8 }}>
      <Space size="middle" style={{ width: '100%' }}>
        <Input 
          prefix={<ApiOutlined />} 
          placeholder="直播间 Room ID" 
          style={{ width: 200 }} 
          value={roomId}
          onChange={(e) => setRoomId(e.target.value)}
          disabled={isConnected}
        />
        <Input.Password 
          prefix={<KeyOutlined />} 
          placeholder="Sessdata (Cookie)" 
          style={{ width: 300 }} 
          value={sessDataInput}
          onChange={(e) => setSessDataInput(e.target.value)}
          disabled={isConnected}
        />
        {!isConnected ? (
            <Button type="primary" onClick={() => handleConnect()} loading={loading}>
                连接房间
            </Button>
        ) : (
            <Button danger icon={<DisconnectOutlined />} onClick={handleDisconnect} loading={loading}>
                断开连接
            </Button>
        )}
      </Space>
    </Card>
  );
};

export default ConnectionManager;
