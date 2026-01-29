import React from 'react';
import { Button, Avatar, Dropdown, Space, Typography, Tag } from 'antd';
import { UserOutlined, SettingOutlined, LogoutOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const TopNav = ({ onOpenSettings }) => {
  // 模拟状态
  const isConnected = false;
  const roomTitle = "-";
  const isLoggedIn = false;
  const username = "未登录";

  const userMenu = {
    items: [
      {
        key: 'logout',
        label: '退出登录',
        icon: <LogoutOutlined />,
      },
    ],
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', height: '100%' }}>
      <Space size="large">
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
        <Dropdown menu={userMenu} disabled={!isLoggedIn}>
          <Space style={{ cursor: 'pointer' }}>
            <Avatar icon={<UserOutlined />} src={null} />
            <Text>{username}</Text>
          </Space>
        </Dropdown>
        <Button 
          type="text" 
          icon={<SettingOutlined style={{ fontSize: '18px' }} />} 
          onClick={onOpenSettings}
        />
      </Space>
    </div>
  );
};

export default TopNav;
