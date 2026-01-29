import React from 'react';
import { Input, Button, Space, Card } from 'antd';
import { ApiOutlined, KeyOutlined } from '@ant-design/icons';

const ConnectionManager = () => {
  return (
    <Card bordered={false} bodyStyle={{ padding: '12px 24px', background: '#f5f5f5', borderRadius: 8 }}>
      <Space size="middle" style={{ width: '100%' }}>
        <Input 
          prefix={<ApiOutlined />} 
          placeholder="直播间 Room ID" 
          style={{ width: 200 }} 
        />
        <Input.Password 
          prefix={<KeyOutlined />} 
          placeholder="Sessdata (Cookie)" 
          style={{ width: 300 }} 
        />
        <Button type="primary">连接房间</Button>
      </Space>
    </Card>
  );
};

export default ConnectionManager;
