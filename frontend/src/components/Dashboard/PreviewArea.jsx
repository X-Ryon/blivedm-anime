import React from 'react';
import { Button, Typography } from 'antd';
import { UpOutlined, DownOutlined, PlayCircleOutlined } from '@ant-design/icons';

const PreviewArea = ({ expanded, onToggle }) => {
  return (
    <div style={{ 
      height: expanded ? 300 : 50, 
      transition: 'height 0.3s cubic-bezier(0.4, 0, 0.2, 1)', 
      background: '#fff', 
      borderTop: '1px solid #f0f0f0',
      position: 'relative',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      width: '100%'
    }}>
      <div style={{ 
        height: 50, 
        flexShrink: 0,
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        borderBottom: expanded ? '1px solid #f0f0f0' : 'none',
        cursor: 'pointer',
        background: '#fafafa',
        userSelect: 'none'
      }}
      onClick={onToggle}
      >
        <Button 
            type="text" 
            icon={expanded ? <DownOutlined /> : <UpOutlined />}
            style={{ pointerEvents: 'none' }} // 让点击事件穿透到 div
        >
            {expanded ? '收起预览' : '展开动画预览'}
        </Button>
      </div>

      <div style={{ 
          flex: 1, 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          background: '#333',
          opacity: expanded ? 1 : 0,
          transition: 'opacity 0.2s ease-in-out',
          pointerEvents: expanded ? 'auto' : 'none'
      }}>
          <div style={{ textAlign: 'center', color: '#fff' }}>
              <PlayCircleOutlined style={{ fontSize: 48, marginBottom: 12, opacity: 0.5 }} />
              <Typography.Title level={5} style={{ color: '#fff', opacity: 0.5 }}>动画预览区域 (预留)</Typography.Title>
          </div>
      </div>
    </div>
  );
};

export default PreviewArea;
