import React, { useRef, useEffect, useState } from 'react';
import { Avatar, Tag, Typography, Space } from 'antd';
import { UserOutlined } from '@ant-design/icons';

const { Text } = Typography;

const ScItem = ({ data }) => {
  const { username, content, avatar, level, time, price } = data;
  
  return (
    <div style={{ 
      display: 'flex', 
      marginBottom: 12, 
      alignItems: 'flex-start',
      padding: '0 8px'
    }}>
      <Avatar icon={<UserOutlined />} src={avatar} size="small" style={{ marginTop: 4, flexShrink: 0 }} />
      <div style={{ marginLeft: 12, maxWidth: 'calc(100% - 44px)' }}>
        <Space size={4} style={{ marginBottom: 2, display: 'flex', alignItems: 'center' }}>
          <Text type="secondary" style={{ fontSize: 12 }}>{username}</Text>
          <Tag color="gold" style={{ fontSize: 10, lineHeight: '16px', height: 18, padding: '0 4px', margin: 0 }}>UL {level}</Tag>
          <Text type="secondary" style={{ fontSize: 10 }}>{time}</Text>
        </Space>
        <div style={{ 
          background: '#E6F7FF', // 统一蓝色
          border: '1px solid #91D5FF',
          borderRadius: '0 12px 12px 12px',
          padding: '8px 12px',
          position: 'relative',
          wordBreak: 'break-word'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: 4, color: '#096dd9' }}>¥ {price}</div>
          <Text>{content}</Text>
        </div>
      </div>
    </div>
  );
};

const ScList = () => {
    const listRef = useRef(null);
    const [mockData, setMockData] = useState(() => {
        return Array.from({ length: 20 }, (_, i) => ({
            id: i + 1,
            username: `RichUser_${i + 1}`,
            content: `主播好棒！支持一下！(第 ${i + 1} 条 SC)`,
            avatar: '',
            level: Math.floor(Math.random() * 20) + 10,
            price: (i + 1) * 30,
            time: `12:${30 + i}:01`
        }));
    });
    const [autoScroll, setAutoScroll] = useState(true);

    // 模拟新数据流入
    useEffect(() => {
        const timer = setInterval(() => {
            setMockData(prev => {
                const nextId = prev.length > 0 ? prev[prev.length - 1].id + 1 : 1;
                const newItem = {
                    id: nextId,
                    username: `NewRichUser_${nextId}`,
                    content: `主播好棒！(第 ${nextId} 条 SC)`,
                    avatar: '',
                    level: 20,
                    price: 100,
                    time: new Date().toLocaleTimeString()
                };
                return [...prev, newItem];
            });
        }, 5000); // 每5秒添加一条

        return () => clearInterval(timer);
    }, []);

    // 滚动处理
    useEffect(() => {
        if (listRef.current && autoScroll) {
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    }, [mockData, autoScroll]);

    // 监听用户手动滚动
    const handleScroll = () => {
        if (listRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = listRef.current;
            const isBottom = scrollHeight - scrollTop - clientHeight < 10;
            setAutoScroll(isBottom);
        }
    };

  return (
    <div style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        background: '#fff', 
        borderRadius: 8, 
        border: '1px solid #f0f0f0',
        height: '100%',
        overflow: 'hidden'
    }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0', fontWeight: 'bold', backgroundColor: '#fafafa' }}>
        SuperChat
      </div>
      <div 
        ref={listRef}
        onScroll={handleScroll}
        style={{ flex: 1, overflowY: 'auto', padding: '12px 0' }}
      >
        {mockData.map(item => <ScItem key={item.id} data={item} />)}
      </div>
    </div>
  );
};

export default ScList;
