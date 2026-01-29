import React, { useRef, useEffect, useState } from 'react';
import { Avatar, Tag, Typography, Space } from 'antd';
import { UserOutlined } from '@ant-design/icons';

const { Text } = Typography;

const getBgColor = (guardLevel) => {
  switch (guardLevel) {
    case 3: return '#E6F7FF'; // 舰长 - 浅蓝
    case 2: return '#F9F0FF'; // 提督 - 浅紫
    case 1: return '#FFF1F0'; // 总督 - 浅红
    default: return '#F5F5F5'; // 普通 - 浅灰
  }
};

const getBorderColor = (guardLevel) => {
    switch (guardLevel) {
      case 3: return '#91D5FF';
      case 2: return '#D3ADF7';
      case 1: return '#FFCCC7';
      default: return '#D9D9D9';
    }
  };

const DanmakuItem = ({ data }) => {
  const { username, content, avatar, level, guardLevel } = data;
  
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
          <Tag color="blue" style={{ fontSize: 10, lineHeight: '16px', height: 18, padding: '0 4px', margin: 0 }}>UL {level}</Tag>
        </Space>
        <div style={{ 
          background: getBgColor(guardLevel), 
          border: `1px solid ${getBorderColor(guardLevel)}`,
          borderRadius: '0 12px 12px 12px',
          padding: '8px 12px',
          position: 'relative',
          wordBreak: 'break-word'
        }}>
          <Text>{content}</Text>
        </div>
      </div>
    </div>
  );
};

const DanmakuList = () => {
    const listRef = useRef(null);
    const [mockData, setMockData] = useState(() => {
        return Array.from({ length: 30 }, (_, i) => ({
            id: i + 1,
            username: `User_${i + 1}`,
            content: i % 3 === 0 ? '这是一条比较长的测试弹幕，用来测试换行效果是否正常，以及气泡是否会自适应高度。' : `测试弹幕 ${i + 1}`,
            avatar: '',
            level: Math.floor(Math.random() * 40) + 1,
            guardLevel: i % 5 === 0 ? 3 : (i % 10 === 0 ? 2 : 0)
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
                    username: `NewUser_${nextId}`,
                    content: `新增弹幕 ${nextId}`,
                    avatar: '',
                    level: Math.floor(Math.random() * 40) + 1,
                    guardLevel: 0
                };
                return [...prev, newItem];
            });
        }, 2000); // 每2秒添加一条

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
            // 如果用户向上滚动（距离底部超过 10px），则取消自动滚动
            // 否则（接近底部），恢复自动滚动
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
        实时弹幕
      </div>
      <div 
        ref={listRef}
        onScroll={handleScroll}
        style={{ flex: 1, overflowY: 'auto', padding: '12px 0' }}
      >
        {mockData.map(item => <DanmakuItem key={item.id} data={item} />)}
      </div>
    </div>
  );
};

export default DanmakuList;
