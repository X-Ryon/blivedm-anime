import React, { useState } from 'react';
import { Layout } from 'antd';
import TopNav from '../components/Dashboard/TopNav';
import ConnectionManager from '../components/Dashboard/ConnectionManager';
import DanmakuList from '../components/Dashboard/MonitorLists/DanmakuList';
import ScList from '../components/Dashboard/MonitorLists/ScList';
import GiftList from '../components/Dashboard/MonitorLists/GiftList';
import PreviewArea from '../components/Dashboard/PreviewArea';
import SettingsPanel from '../components/Dashboard/SettingsPanel';

const { Header, Content } = Layout;

const Admin = () => {
  const [settingsVisible, setSettingsVisible] = useState(false);
  const [previewExpanded, setPreviewExpanded] = useState(false);

  return (
    <Layout style={{ 
        height: '100vh', 
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column' 
    }}>
      <Header style={{ 
          background: '#fff', 
          padding: '0 20px', 
          height: 'auto',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 1,
          flexShrink: 0
      }}>
        <div style={{ height: 64 }}>
            <TopNav onOpenSettings={() => setSettingsVisible(true)} />
        </div>
        <div style={{ paddingBottom: 16 }}>
            <ConnectionManager />
        </div>
      </Header>

      <Content style={{ 
          padding: '16px 20px', 
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          flex: 1,
          minHeight: 0 // 关键：允许 flex item 压缩到内容以下
      }}>
        <div style={{ display: 'flex', flex: 1, gap: '16px', overflow: 'hidden', minHeight: 0 }}>
           <DanmakuList />
           <ScList />
           <GiftList />
        </div>
      </Content>

      <div style={{ flexShrink: 0, zIndex: 2, boxShadow: '0 -2px 8px rgba(0,0,0,0.05)' }}>
        <PreviewArea 
            expanded={previewExpanded} 
            onToggle={() => setPreviewExpanded(!previewExpanded)} 
        />
      </div>

      <SettingsPanel visible={settingsVisible} onClose={() => setSettingsVisible(false)} />
    </Layout>
  );
};

export default Admin;
