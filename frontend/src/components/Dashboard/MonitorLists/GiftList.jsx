import React, { useState, useEffect, useMemo } from 'react';
import { Tag, Typography } from 'antd';
import { GiftOutlined, EyeOutlined, EyeInvisibleOutlined } from '@ant-design/icons';
import useDanmakuStore from '../../../store/useDanmakuStore';
import useCachedImage from '../../../hooks/useCachedImage';
import useDynamicList from '../../../hooks/useDynamicList';
import { giftApi } from '../../../services/api';

const { Text } = Typography;

// --- 样式配置 ---
// 在此处自定义礼物记录的行间距和内边距
// padding: '上下 左右'
const ROW_PADDING = '12px 16px'; 
const ROW_LINE_HEIGHT = '28px';

const CachedGiftImage = ({ giftName, giftImg, defaultIcon }) => {
    // 1. Get Metadata from store
    const giftMetadata = useDanmakuStore(state => state.giftMetadata);
    
    // Priority: 1. giftImg from prop (realtime message) 2. metadata lookup
    // Add safe access to giftMetadata
    const imgUrl = giftImg || (giftMetadata ? giftMetadata[giftName] : null);

    // 2. Use cached image hook
    const cachedUrl = useCachedImage(imgUrl, 'gift_icon'); 

    if (cachedUrl) {
        return <img src={cachedUrl} alt={giftName} style={{ width: 24, height: 24, objectFit: 'contain', verticalAlign: 'middle' }} />;
    }
    
    return defaultIcon || <GiftOutlined style={{ color: '#eb2f96' }} />;
};

const GiftItem = React.memo(({ data }) => {
  const { username, giftName, count, price, level, time, giftImg } = data;
  
  // Layout: Username(Bold) | Level | "赠送" | GiftImg | GiftName x Count | Price | Time
  return (
    <div style={{ padding: ROW_PADDING, display: 'flex', alignItems: 'center', borderBottom: '1px solid #f0f0f0', lineHeight: ROW_LINE_HEIGHT }}>
        {/* 1. Username (Bold) */}
        <Text strong style={{ fontSize: 14, marginRight: 8, color: '#1890ff' }}>{username}</Text>
        
        {/* 2. Level */}
        <Tag color="orange" style={{ fontSize: 10, lineHeight: '16px', height: 18, padding: '0 4px', margin: '0 8px 0 0', border: 'none' }}>Lv {level}</Tag>
        
        {/* 3. Action Text */}
        <Text type="secondary" style={{ fontSize: 12, marginRight: 8 }}>赠送</Text>
        
        {/* 4. Gift Image & Name & Count */}
        <div style={{ display: 'flex', alignItems: 'center', marginRight: 'auto' }}>
             <div style={{ marginRight: 6, display: 'flex', alignItems: 'center' }}>
                <CachedGiftImage giftName={giftName} giftImg={giftImg} />
             </div>
             <Text style={{ color: '#eb2f96', fontWeight: 500, fontSize: 14 }}>{giftName}</Text>
             <Text style={{ marginLeft: 6, color: '#eb2f96', fontWeight: 600, fontSize: 14 }}>x {count}</Text>
        </div>

        {/* 5. Price */}
        <Text type="secondary" style={{ fontSize: 12, marginRight: 16 }}>¥ {price}</Text>

        {/* 6. Time */}
        <Text type="secondary" style={{ fontSize: 12, minWidth: 130, textAlign: 'right' }}>{time}</Text>
    </div>
  );
});

const GiftList = () => {
    const giftList = useDanmakuStore(state => state.giftList);
    const searchText = useDanmakuStore(state => state.searchText);
    const totalRevenue = useDanmakuStore(state => state.totalRevenue);
    const giftMetadata = useDanmakuStore(state => state.giftMetadata);
    const updateGiftMetadata = useDanmakuStore(state => state.updateGiftMetadata);
    
    const [showRevenue, setShowRevenue] = useState(true);

    const filteredList = useMemo(() => {
        if (!searchText) return giftList;
        const lowerText = searchText.toLowerCase();
        return giftList.filter(item =>
            (item.username && item.username.toLowerCase().includes(lowerText))
        );
    }, [giftList, searchText]);

    // 使用动态列表 Hook：最大渲染200条，每次加载30条历史
    const { listRef, renderList, handleScroll } = useDynamicList(filteredList, 50, 30);

    // Initial fetch for gift metadata if empty
    useEffect(() => {
        const fetchMetadata = async () => {
            if (!giftMetadata || Object.keys(giftMetadata).length === 0) {
                try {
                    const res = await giftApi.getGiftList();
                    if (res.code === 200 && Array.isArray(res.data)) {
                        updateGiftMetadata(res.data);
                    }
                } catch (e) {
                    console.error("Failed to fetch gift metadata:", e);
                }
            }
        };
        fetchMetadata();
    }, [giftMetadata, updateGiftMetadata]);

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
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0', fontWeight: 'bold', backgroundColor: '#fafafa', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>礼物记录</span>
        <div style={{ display: 'flex', alignItems: 'center', fontSize: 14, fontWeight: 'normal' }}>
             <span style={{ marginRight: 8, color: '#6e6e6e', fontWeight: 'bold' }}>
                {showRevenue ? `¥${totalRevenue.toFixed(2)}` : '****'}
             </span>
             {showRevenue ? 
                <EyeOutlined onClick={() => setShowRevenue(false)} style={{ cursor: 'pointer', color: '#8c8c8c' }} /> : 
                <EyeInvisibleOutlined onClick={() => setShowRevenue(true)} style={{ cursor: 'pointer', color: '#8c8c8c' }} />
             }
        </div>
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
