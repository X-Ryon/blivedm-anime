import React, { useEffect, useState, useRef } from 'react';
import { Modal, Button, Spin, message, Typography } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { authApi } from '../../services/api';
import useUserStore from '../../store/useUserStore';

const { Text } = Typography;

const LoginModal = ({ open, onCancel }) => {
    const [loading, setLoading] = useState(true);
    const [qrCodeUrl, setQrCodeUrl] = useState('');
    const [qrCodeKey, setQrCodeKey] = useState('');
    const qrCodeKeyRef = useRef(''); // 使用 Ref 追踪最新的 key，防止闭包导致的旧值轮询
    const [status, setStatus] = useState('loading'); // loading, waiting, scanned, expired, success
    const timerRef = useRef(null);
    const handleLoginSuccess = useUserStore(state => state.handleLoginSuccess);

    const fetchQrcode = async () => {
        // 清除之前的轮询定时器
        if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }
        
        setLoading(true);
        setStatus('loading');
        qrCodeKeyRef.current = ''; // 清空 Ref
        setQrCodeKey(''); 

        try {
            const res = await authApi.getQrcode();
            if (res.code === 200) {
                // 后端返回的是相对路径 /static/qrcode/xxx.png
                // 我们需要拼接完整的 URL
                // 假设后端运行在 localhost:8000
                const backendOrigin = 'http://localhost:8000';
                setQrCodeUrl(`${backendOrigin}${res.data.img_path}`);
                
                const newKey = res.data.qrcode_key;
                setQrCodeKey(newKey);
                qrCodeKeyRef.current = newKey; // 更新 Ref
                
                setStatus('waiting');
            } else {
                console.error('Failed to get QR code:', res);
                message.error(`获取二维码失败: ${res.message || '未知错误'}`);
            }
        } catch (error) {
            console.error('Error fetching QR code:', error);
            message.error(`获取二维码失败: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (open) {
            fetchQrcode();
        } else {
            // 关闭弹窗时清除定时器
            if (timerRef.current) {
                clearInterval(timerRef.current);
                timerRef.current = null;
            }
        }
        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        };
    }, [open]);

    // 轮询逻辑
    useEffect(() => {
        // 确保状态为 waiting 或 scanned，且有 key 时才轮询
        if ((status === 'waiting' || status === 'scanned') && qrCodeKey) {
            // 先清除可能存在的旧定时器
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }

            timerRef.current = setInterval(async () => {
                // 双重保障：使用 Ref 获取最新的 key，防止闭包捕获旧值
                const currentKey = qrCodeKeyRef.current;
                if (!currentKey) return;

                try {
                    console.log(`Polling status for key: ${currentKey}`);
                    const res = await authApi.pollLoginStatus(currentKey);
                    if (res.code === 200) {
                        const { status: loginStatus, data, sessdata } = res.data;
                        
                        if (loginStatus === 'success') {
                            message.success(`登录成功: ${data.user_name}`);
                            handleLoginSuccess(data, sessdata);
                            onCancel(); // 关闭弹窗
                        } else if (loginStatus === 'scanned') {
                            setStatus('scanned');
                        } else if (loginStatus === 'expired') {
                            setStatus('expired');
                            clearInterval(timerRef.current);
                        }
                    } else {
                        // 错误处理，如果是 86038 (过期)
                         if (res.code === 86038) {
                            setStatus('expired');
                            clearInterval(timerRef.current);
                         }
                    }
                } catch (error) {
                    console.error('Poll error:', error);
                }
            }, 3000);
        } else {
            if (timerRef.current) {
                clearInterval(timerRef.current);
                timerRef.current = null;
            }
        }

        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        };
    }, [status, qrCodeKey, handleLoginSuccess, onCancel]);

    const handleRefresh = () => {
        fetchQrcode();
    };

    return (
        <Modal
            title="扫码登录 Bilibili"
            open={open}
            onCancel={onCancel}
            footer={null}
            width={360}
            centered
        >
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px 0' }}>
                {loading ? (
                    <Spin size="large" tip="正在获取二维码..." />
                ) : (
                    <>
                        <div style={{ position: 'relative', width: 200, height: 200, marginBottom: 20 }}>
                            {qrCodeUrl && (
                                <img 
                                    src={qrCodeUrl} 
                                    alt="Login QR Code" 
                                    style={{ width: '100%', height: '100%', opacity: status === 'expired' ? 0.3 : 1 }} 
                                />
                            )}
                            {status === 'expired' && (
                                <div style={{
                                    position: 'absolute',
                                    top: 0,
                                    left: 0,
                                    width: '100%',
                                    height: '100%',
                                    display: 'flex',
                                    justifyContent: 'center',
                                    alignItems: 'center',
                                    background: 'rgba(255,255,255,0.6)'
                                }}>
                                    <Button type="primary" shape="circle" icon={<ReloadOutlined />} onClick={handleRefresh} size="large" />
                                </div>
                            )}
                            {status === 'scanned' && (
                                <div style={{
                                    position: 'absolute',
                                    top: 0,
                                    left: 0,
                                    width: '100%',
                                    height: '100%',
                                    display: 'flex',
                                    justifyContent: 'center',
                                    alignItems: 'center',
                                    background: 'rgba(255,255,255,0.8)'
                                }}>
                                    <Text strong style={{ fontSize: 16 }}>已扫码，请在手机上确认</Text>
                                </div>
                            )}
                        </div>
                        
                        {status === 'expired' ? (
                            <Text type="danger">二维码已过期，请刷新</Text>
                        ) : status === 'scanned' ? (
                            <Text type="success">扫码成功</Text>
                        ) : (
                            <Text type="secondary">请使用 哔哩哔哩客户端 扫码登录</Text>
                        )}
                        
                        <div style={{ marginTop: 20 }}>
                            <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
                                刷新二维码
                            </Button>
                        </div>
                    </>
                )}
            </div>
        </Modal>
    );
};

export default LoginModal;
