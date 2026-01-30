import React from 'react';
import { Avatar, Tag, Typography, Space } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import useDanmakuStore from '../../../store/useDanmakuStore';
import useCachedImage from '../../../hooks/useCachedImage';
import useDynamicList from '../../../hooks/useDynamicList';

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

const DanmakuItem = React.memo(({ data }) => {
  const { username, content, avatar, level, guardLevel } = data;
  const avatarUrl = useCachedImage(avatar);
  
  return (
    <div style={{ 
      display: 'flex', 
      marginBottom: 12, 
      alignItems: 'flex-start',
      padding: '0 8px'
    }}>
      <Avatar icon={<UserOutlined />} src={avatarUrl} size="small" style={{ marginTop: 4, flexShrink: 0 }} />
      <div style={{ marginLeft: 12, maxWidth: 'calc(100% - 44px)' }}>
        <Space size={4} style={{ marginBottom: 2, display: 'flex', alignItems: 'center' }}>
          <Text type="secondary" style={{ fontSize: 12 }}>{username}</Text>
          <Tag color="blue" style={{ fontSize: 10, lineHeight: '16px', height: 18, padding: '0 4px', margin: 0 }}>Lv {level}</Tag>
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
});

const DanmakuList = () => {
    const danmakuList = useDanmakuStore(state => state.danmakuList);
    // 使用动态列表 Hook：最大渲染200条，每次加载30条历史
    const { listRef, renderList, handleScroll } = useDynamicList(danmakuList, 50, 30);

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
            <div style={{ 
                padding: '12px 16px', 
                borderBottom: '1px solid #f0f0f0',
                fontWeight: 500
            }}>
                弹幕列表
            </div>
            <div 
                ref={listRef}
                onScroll={handleScroll}
                style={{ 
                    flex: 1, 
                    overflowY: 'auto', 
                    padding: '12px' 
                }}
            >
                {renderList.map(item => (
                    <DanmakuItem key={item.id} data={item} />
                ))}
            </div>
        </div>
    );
};

export default DanmakuList;
