import React, { useState, useEffect } from 'react';
import { Button, Avatar, Dropdown, Space, Typography, Tag, Modal } from 'antd';
import { UserOutlined, SettingOutlined, LogoutOutlined, LoginOutlined, MinusCircleOutlined } from '@ant-design/icons';
import LoginModal from './LoginModal';
import useUserStore from '../../store/useUserStore';
import useDanmakuStore from '../../store/useDanmakuStore';
import { authApi } from '../../services/api';
import useCachedImage from '../../hooks/useCachedImage';

const { Title, Text } = Typography;

const CachedAvatar = ({ src, size, icon }) => {
    const cachedUrl = useCachedImage(src);
    return <Avatar src={cachedUrl} size={size} icon={icon} />;
};

const TopNav = ({ onOpenSettings }) => {
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [savedUsers, setSavedUsers] = useState([]);
  
  const { 
    isLoggedIn, 
    userInfo, 
    logout, 
    fetchConfig,
    handleLoginSuccess
  } = useUserStore();

  const isConnected = useDanmakuStore(state => state.isConnected);
  const roomTitle = useDanmakuStore(state => state.roomTitle);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const fetchSavedUsers = async () => {
    try {
      const res = await authApi.getUsersList();
      if (res.code === 200) {
        setSavedUsers(res.data);
      }
    } catch (error) {
      console.error('Failed to fetch saved users:', error);
    }
  };

  useEffect(() => {
    if (!isLoggedIn) {
        // Use setTimeout to avoid synchronous setState warning
        setTimeout(() => {
            fetchSavedUsers();
        }, 0);
    }
  }, [isLoggedIn]);


  const handleDeleteUser = (e, user) => {
    e.stopPropagation();
    Modal.confirm({
      title: '移除账号',
      content: `确定要移除账号 "${user.user_name}" 吗？`,
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          const res = await authApi.deleteUser(user.uid);
          if (res.code === 200) {
            fetchSavedUsers();
          }
        } catch (error) {
          console.error('Failed to delete user:', error);
        }
      },
    });
  };

  const handleMenuClick = (e) => {
    if (e.key === 'login') {
      setIsLoginModalOpen(true);
    } else if (e.key === 'logout') {
      logout();
    } else if (e.key.startsWith('user_')) {
      const uid = e.key.split('_')[1];
      const user = savedUsers.find(u => u.uid.toString() === uid);
      if (user) {
        handleLoginSuccess(user, user.sessdata);
      }
    }
  };

  const userMenuItems = isLoggedIn ? [
    {
      key: 'logout',
      label: '退出登录',
      icon: <LogoutOutlined />,
    }
  ] : [
    ...savedUsers.map(user => ({
      key: `user_${user.uid}`,
      label: (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', minWidth: '160px' }}>
          <Space>
            <CachedAvatar src={user.face_img} size="small" icon={<UserOutlined />} />
            <Text ellipsis style={{ maxWidth: 100 }}>{user.user_name}</Text>
          </Space>
          <Button 
            type="text" 
            danger 
            size="small" 
            icon={<MinusCircleOutlined />} 
            onClick={(e) => handleDeleteUser(e, user)}
          />
        </div>
      ),
    })),
    ...(savedUsers.length > 0 ? [{ type: 'divider' }] : []),
    {
      key: 'login',
      label: '扫码登录',
      icon: <LoginOutlined />,
    }
  ];

  const userMenu = {
    items: userMenuItems,
    onClick: handleMenuClick,
  };

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', height: '100%' }}>
        <Space size="large" align="center">
          <Title level={4} style={{ margin: 0 }}>Bilibili 直播弹幕姬</Title>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Tag color={isConnected ? 'green' : 'default'} style={{ margin: 0, marginRight: 8 }}>
              {isConnected ? '已连接' : '未连接'}
            </Tag>
            <Text 
              type="secondary" 
              style={{ maxWidth: 200, margin: 0 }} 
              ellipsis={{ tooltip: roomTitle }}
            >
              {roomTitle}
            </Text>
          </div>
        </Space>

        <Space size="large">
          <Dropdown menu={userMenu}>
            <Space style={{ cursor: 'pointer' }}>
              <CachedAvatar src={isLoggedIn ? userInfo?.face_img : null} icon={<UserOutlined />} />
              <Text>{isLoggedIn ? userInfo?.user_name : "未登录"}</Text>
            </Space>
          </Dropdown>
          <Button 
            type="text" 
            icon={<SettingOutlined style={{ fontSize: '18px' }} />} 
            onClick={onOpenSettings}
          />
        </Space>
      </div>

      <LoginModal 
        open={isLoginModalOpen} 
        onCancel={() => setIsLoginModalOpen(false)} 
      />
    </>
  );
};

export default TopNav;
