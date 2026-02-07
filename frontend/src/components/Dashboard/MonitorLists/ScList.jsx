import React, { useMemo } from 'react';
import { Tag, Typography, Space } from 'antd';
import useDanmakuStore from '../../../store/useDanmakuStore';
import useDynamicList from '../../../hooks/useDynamicList';

const { Text } = Typography;

const getScStyle = (price) => {
  if (price < 50) {
    // 蓝色 - 49元以下 - 加深
    return {
      bg: '#0066ffff', // Blue-4
      border: '#0061bb', // Blue-6
      text: '#ffffff'  // Blue-10
    };
  } else if (price < 100) {
    // 绿色 - 50-99元 - 加深
    return {
      bg: '#00af17', // Lime-5
      border: '#005f1d', // Lime-6
      text: '#ffffff' // Dark Green
    };
  } else if (price < 1000) {
    // 金色 - 100-999元 - 加深
    return {
      bg: '#ecc100ff', // Gold-6
      border: '#976500', // Gold-8
      text: '#ffffff' // Dark Gold
    };
  } else {
    // 红色 - 1000元以上 - 加深
    return {
      bg: '#c92f00', // Red-5
      border: '#6b0005', // Red-6
      text: '#ffffff' // Red-10
    };
  }
};

const ScItem = React.memo(({ data }) => {
  const { username, content, level, time, price } = data;
  const style = getScStyle(Number(price));
  
  return (
    <div style={{ 
      display: 'flex', 
      marginBottom: 12, 
      alignItems: 'flex-start',
      padding: '0 8px'
    }}>
      <div style={{ marginLeft: 0, width: '100%' }}>
        <Space size={4} style={{ marginBottom: 2, display: 'flex', alignItems: 'center' }}>
          <div style={{ 
            background: '#f0f2f5', 
            padding: '2px 8px', 
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <Text style={{ fontSize: 14, fontWeight: 'bold', color: '#1890ff' }}>{username}</Text>
            <Tag color="gold" style={{ fontSize: 10, lineHeight: '16px', height: 18, padding: '0 4px', margin: 0 }}>Lv {level}</Tag>
          </div>
          <Text type="secondary" style={{ fontSize: 10 }}>{time}</Text>
        </Space>
        <div style={{ 
          background: style.bg,
          border: `1px solid ${style.border}`,
          borderRadius: '12px',
          padding: '8px 12px',
          position: 'relative',
          wordBreak: 'break-word'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: 4, color: style.text }}>¥ {price}</div>
          <Text style={{ color: style.text, fontWeight: 'bold', fontSize: 16 }}>{content}</Text>
        </div>
      </div>
    </div>
  );
});

const ScList = () => {
    const scList = useDanmakuStore(state => state.scList);
    const searchText = useDanmakuStore(state => state.searchText);

    const filteredList = useMemo(() => {
        if (!searchText) return scList;
        const lowerText = searchText.toLowerCase();
        return scList.filter(item =>
            (item.content && item.content.toLowerCase().includes(lowerText)) ||
            (item.username && item.username.toLowerCase().includes(lowerText))
        );
    }, [scList, searchText]);

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
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0', fontWeight: 'bold', backgroundColor: '#fafafa' }}>
        醒目留言 (SC)
      </div>
      <div 
        ref={listRef}
        onScroll={handleScroll}
        style={{ flex: 1, overflowY: 'auto', padding: '12px' }}
      >
        {renderList.map(item => <ScItem key={item.id} data={item} />)}
      </div>
    </div>
  );
};

export default ScList;
