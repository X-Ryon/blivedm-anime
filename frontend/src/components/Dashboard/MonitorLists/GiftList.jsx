import React from 'react';
import { Avatar, Tag, Typography, Space } from 'antd';
import { UserOutlined, GiftOutlined } from '@ant-design/icons';
import useDanmakuStore from '../../../store/useDanmakuStore';
import useCachedImage from '../../../hooks/useCachedImage';
import useDynamicList from '../../../hooks/useDynamicList';

const { Text } = Typography;

const GiftItem = React.memo(({ data }) => {
  const { username, giftName, count, price, avatar, level, time } = data;
  const avatarUrl = useCachedImage(avatar);
  
  return (
    <div style={{ padding: '8px 12px', display: 'flex', borderBottom: '1px solid #f0f0f0' }}>
      <div style={{ marginRight: 16 }}>
        <Avatar icon={<UserOutlined />} src={avatarUrl} size="small" />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ marginBottom: 4 }}>
          <Space size={4}>
            <Text style={{ fontSize: 12 }}>{username}</Text>
            <Tag color="orange" style={{ fontSize: 10, lineHeight: '16px', height: 18, padding: '0 4px', margin: 0 }}>Lv {level}</Tag>
            <Text type="secondary" style={{ fontSize: 10 }}>{time}</Text>
          </Space>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
                <GiftOutlined style={{ color: '#eb2f96' }} />
                <Text strong style={{ color: '#eb2f96' }}>{giftName} x {count}</Text>
            </Space>
            <Text type="secondary" style={{ fontSize: 11 }}>¥ {price}</Text>
        </div>
      </div>
    </div>
  );
});

const GiftList = () => {
    const giftList = useDanmakuStore(state => state.giftList);
    // 使用动态列表 Hook：最大渲染200条，每次加载30条历史
    const { listRef, renderList, handleScroll } = useDynamicList(giftList, 50, 30);

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
        {renderList.map(item => (
            <GiftItem key={item.id} data={item} />
        ))}
      </div>
    </div>
  );
};

export default GiftList;
