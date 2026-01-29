import React from 'react';
import { Drawer, Form, Checkbox, Select, Button, Upload, List, Typography, Space, Divider } from 'antd';
import { UploadOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';

const { Option } = Select;
const { Title } = Typography;

const SettingsPanel = ({ visible, onClose }) => {
  return (
    <Drawer
      title="设置"
      placement="right"
      onClose={onClose}
      open={visible}
      width={400}
    >
      <Form layout="vertical">
        <Title level={5}>通用设置</Title>
        <Form.Item name="autoLogin" valuePropName="checked" style={{ marginBottom: 8 }}>
          <Checkbox>自动登录账号</Checkbox>
        </Form.Item>
        <Form.Item name="autoConnect" valuePropName="checked">
          <Checkbox>自动连接房间</Checkbox>
        </Form.Item>

        <Divider />

        <Title level={5}>数据管理</Title>
        <Form.Item label="清理历史记录范围">
          <Select defaultValue="7">
            <Option value="7">7天前</Option>
            <Option value="30">30天前</Option>
            <Option value="90">90天前</Option>
            <Option value="180">180天前</Option>
            <Option value="all">全部</Option>
          </Select>
        </Form.Item>
        <Button danger icon={<DeleteOutlined />} block>清理弹幕礼物缓存</Button>

        <Divider />

        <Title level={5}>素材配置</Title>
        <Button icon={<UploadOutlined />} block style={{ marginBottom: 12 }}>上传素材文件</Button>
        
        {/* 这里只是简单展示，因为没有真实数据 */}
        <Form.Item label="礼物 - 动画映射">
            <div style={{ background: '#f5f5f5', padding: 12, borderRadius: 6, textAlign: 'center', color: '#999' }}>
                (列表暂无数据)
            </div>
        </Form.Item>

        <Form.Item label="舰队 - 形象映射">
            <div style={{ background: '#f5f5f5', padding: 12, borderRadius: 6, textAlign: 'center', color: '#999' }}>
                (列表暂无数据)
            </div>
        </Form.Item>

        <Divider />
        
        <Button type="dashed" icon={<ReloadOutlined />} block>恢复默认设置</Button>
      </Form>
    </Drawer>
  );
};

export default SettingsPanel;
