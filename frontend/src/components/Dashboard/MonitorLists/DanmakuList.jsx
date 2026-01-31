import React, { useMemo } from 'react';
import { Avatar, Tag, Typography, Space, Input } from 'antd';
import { UserOutlined, SearchOutlined } from '@ant-design/icons';
import useDanmakuStore from '../../../store/useDanmakuStore';
import useCachedImage from '../../../hooks/useCachedImage';
import useDynamicList from '../../../hooks/useDynamicList';

const { Text } = Typography;

const getBgColor = (guardLevel) => {
  switch (guardLevel) {
    case 3: return '#BAE7FF'; // 舰长 - 加深蓝
    case 2: return '#EFDBFF'; // 提督 - 加深紫
    case 1: return '#FFD8D6'; // 总督 - 加深红
    default: return '#F5F5F5'; // 普通 - 浅灰
  }
};

const getBorderColor = (guardLevel) => {
    switch (guardLevel) {
      case 3: return '#69C0FF';
      case 2: return '#B37FEB';
      case 1: return '#FF85C0';
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
      <Avatar 
        icon={<UserOutlined />} 
        src={avatarUrl} 
        shape="square" 
        size={40} 
        style={{ marginTop: 4, flexShrink: 0, borderRadius: 8 }}
      >
        {!avatarUrl && username ? username[0] : null}
      </Avatar>
      <div style={{ marginLeft: 12, maxWidth: 'calc(100% - 52px)' }}>
        <Space size={4} style={{ marginBottom: 2, display: 'flex', alignItems: 'center' }}>
          <Text type="secondary" style={{ fontSize: 14, fontWeight: 'bold' }}>{username}</Text>
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
    const searchText = useDanmakuStore(state => state.searchText);
    const setSearchText = useDanmakuStore(state => state.setSearchText);

    const filteredList = useMemo(() => {
        if (!searchText) return danmakuList;
        const lowerText = searchText.toLowerCase();
        return danmakuList.filter(item => 
            (item.content && item.content.toLowerCase().includes(lowerText)) ||
            (item.username && item.username.toLowerCase().includes(lowerText))
        );
    }, [danmakuList, searchText]);

    // 使用动态列表 Hook：最大渲染200条，每次加载30条历史
    const { listRef, renderList, handleScroll } = useDynamicList(filteredList, 50, 30);

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
                fontWeight: 500,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <span>弹幕列表</span>
                <Input 
                    placeholder="搜索内容/用户..." 
                    allowClear
                    prefix={<SearchOutlined style={{ color: 'rgba(0,0,0,.25)' }} />}
                    size="small"
                    style={{ width: 200 }}
                    value={searchText}
                    onChange={e => setSearchText(e.target.value)}
                />
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
