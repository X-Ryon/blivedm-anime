import React, { useRef, useEffect, useState } from 'react';
import { List, Avatar, Tag, Typography, Space } from 'antd';
import { UserOutlined, GiftOutlined } from '@ant-design/icons';

const { Text } = Typography;

const GiftItem = ({ data }) => {
  const { username, giftName, count, price, avatar, level, time } = data;
  
  return (
    <List.Item style={{ padding: '8px 12px' }}>
      <List.Item.Meta
        avatar={<Avatar icon={<UserOutlined />} src={avatar} size="small" />}
        title={
          <Space size={4}>
            <Text style={{ fontSize: 12 }}>{username}</Text>
            <Tag color="orange" style={{ fontSize: 10, lineHeight: '16px', height: 18, padding: '0 4px', margin: 0 }}>UL {level}</Tag>
            <Text type="secondary" style={{ fontSize: 10 }}>{time}</Text>
          </Space>
        }
        description={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Space>
                    <GiftOutlined style={{ color: '#eb2f96' }} />
                    <Text strong style={{ color: '#eb2f96' }}>{giftName} x {count}</Text>
                </Space>
                <Text type="secondary" style={{ fontSize: 11 }}>¥ {price}</Text>
            </div>
        }
      />
    </List.Item>
  );
};

const GiftList = () => {
    const listRef = useRef(null);
    const [mockData, setMockData] = useState(() => {
        return Array.from({ length: 20 }, (_, i) => ({
            id: i + 1,
            username: `Fan_${i + 1}`,
            giftName: i % 2 === 0 ? '辣条' : '小电视',
            count: (i + 1) * 10,
            price: i % 2 === 0 ? (i + 1) : (i + 1) * 1245,
            avatar: '',
            level: Math.floor(Math.random() * 40) + 1,
            time: `12:${30 + i}:05`
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
                    username: `NewFan_${nextId}`,
                    giftName: 'B坷垃',
                    count: 99,
                    price: 9900,
                    avatar: '',
                    level: 50,
                    time: new Date().toLocaleTimeString()
                };
                return [...prev, newItem];
            });
        }, 3000); // 每3秒添加一条

        return () => clearInterval(timer);
    }, []);

    // 滚动处理
    // 注意：List 组件的滚动容器是其内部的 div，或者我们可以包裹一层 div 来控制滚动
    // 这里我们直接控制外层 div 的滚动
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
        礼物 / 上舰
      </div>
      <div 
        ref={listRef}
        onScroll={handleScroll}
        style={{ flex: 1, overflowY: 'auto', padding: 0 }}
      >
        <List
            dataSource={mockData}
            renderItem={item => <GiftItem data={item} />}
            split={true}
        />
      </div>
    </div>
  );
};

export default GiftList;
