import React, { useRef, useEffect, useState } from 'react';
import { List, Avatar, Tag, Typography, Space } from 'antd';
import { UserOutlined, GiftOutlined } from '@ant-design/icons';
import useDanmakuStore from '../../../store/useDanmakuStore';
import api from '../../../services/api';

const { Text } = Typography;

const getAvatarUrl = (url) => {
  if (!url) return null;
  return `${api.defaults.baseURL}/proxy/image?url=${encodeURIComponent(url)}`;
};

const GiftItem = ({ data }) => {
  const { username, giftName, count, price, avatar, level, time } = data;
  
  return (
    <List.Item style={{ padding: '8px 12px' }}>
      <List.Item.Meta
        avatar={<Avatar icon={<UserOutlined />} src={getAvatarUrl(avatar)} size="small" />}
        title={
          <Space size={4}>
            <Text style={{ fontSize: 12 }}>{username}</Text>
            <Tag color="orange" style={{ fontSize: 10, lineHeight: '16px', height: 18, padding: '0 4px', margin: 0 }}>Lv {level}</Tag>
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
    const { giftList } = useDanmakuStore();
    const [autoScroll, setAutoScroll] = useState(true);

    // 滚动处理
    useEffect(() => {
        if (listRef.current && autoScroll) {
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    }, [giftList, autoScroll]);

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
        礼物记录
      </div>
      <div 
        ref={listRef}
        onScroll={handleScroll}
        style={{ flex: 1, overflowY: 'auto' }}
      >
        <List
            itemLayout="horizontal"
            dataSource={giftList}
            renderItem={item => <GiftItem data={item} />}
        />
      </div>
    </div>
  );
};

export default GiftList;
