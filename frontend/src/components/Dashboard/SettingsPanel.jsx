import React, { useEffect, useState, useMemo } from 'react';
import { Drawer, Form, Checkbox, Select, Button, Input, Space, Divider, message, Spin, Popconfirm, Table, Typography } from 'antd';
import { ReloadOutlined, LoadingOutlined } from '@ant-design/icons';
import useUserStore from '../../store/useUserStore';
import { debounce } from '../../utils/debounce';
import { giftApi, resourceApi, systemApi } from '../../services/api';

const { Option } = Select;
const { Title, Text } = Typography;

const SettingsPanel = ({ visible, onClose }) => {
  const [form] = Form.useForm();
  const { config, updateConfig, resetConfig } = useUserStore();
  const [saving, setSaving] = useState(false);
  
  // Data for tables
  const [giftList, setGiftList] = useState([]);
  const [assetList, setAssetList] = useState([]);
  const [loadingData, setLoadingData] = useState(false);
  const [localGiftAnimations, setLocalGiftAnimations] = useState([]);
  const [searchText, setSearchText] = useState('');

  // Fetch data on open
  useEffect(() => {
    if (visible) {
        fetchData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible]);

  const fetchData = async () => {
      setLoadingData(true);
      try {
          const [giftsRes, assetsRes, configRes] = await Promise.all([
              giftApi.getGiftList(),
              resourceApi.getAssets(),
              systemApi.getConfig()
          ]);
          
          if (giftsRes.code === 200 && Array.isArray(giftsRes.data)) {
            setGiftList(giftsRes.data);
          }
          if (assetsRes.code === 200 && Array.isArray(assetsRes.data)) {
            setAssetList(assetsRes.data);
          }
          if (configRes.code === 200 && configRes.data) {
              const fetchedConfig = configRes.data;
              // Update store config
              useUserStore.setState({ config: fetchedConfig });
              // Update form and local state
              form.setFieldsValue(fetchedConfig);
              setLocalGiftAnimations(fetchedConfig.resources?.gift_animations || []);
          }
      } catch (e) {
          message.error(`加载配置数据失败: ${e.message}`);
      } finally {
          setLoadingData(false);
      }
  };

  // Sync form with config
  useEffect(() => {
    if (visible && config) {
      form.setFieldsValue(config);
      setLocalGiftAnimations(config.resources?.gift_animations || []);
    }
  }, [visible, config, form]);

  // Debounced save function
  const debouncedSave = useMemo(
    () =>
      debounce(async (values) => {
        setSaving(true);
        try {
          const currentConfig = useUserStore.getState().config;
          if (!currentConfig) return;
          
          // Deep merge config
          const newConfig = {
            ...currentConfig,
            system: {
              ...currentConfig.system,
              ...values.system,
            },
            resources: {
              ...currentConfig.resources,
              ...values.resources,
              // Use explicit gift animations from values (which we manually sync) or fallback to current
              gift_animations: values.resources?.gift_animations || currentConfig.resources?.gift_animations || [],
              guard_skins: {
                  ...currentConfig.resources?.guard_skins,
                  ...values.resources?.guard_skins
              }
            }
          };

          await updateConfig(newConfig);
          message.success({ content: '设置已保存', key: 'save_settings', duration: 2 });
        } catch (error) {
          message.error({ content: `保存失败: ${error.message}`, key: 'save_settings' });
        } finally {
          setSaving(false);
        }
      }, 1000),
    [updateConfig]
  );

  const handleValuesChange = (changedValues, allValues) => {
    // If auto_login or auto_connect is unchecked, clear the corresponding last_* value
    // We modify allValues directly before passing to debouncedSave
    // Note: allValues contains the structure { system: { auto_login: ..., ... }, ... }
    
    if (changedValues.system) {
        if (changedValues.system.auto_login === false) {
            // Need to ensure system object exists (it should)
             if (allValues.system) {
                allValues.system.last_uid = "";
             }
        }
        if (changedValues.system.auto_connect === false) {
             if (allValues.system) {
                allValues.system.last_room_id = "";
             }
        }
    }

    setSaving(true);
    debouncedSave(allValues);
  };

  const handleReset = async () => {
    try {
      setSaving(true);
      const success = await resetConfig();
      if (success) {
        message.success('已恢复默认设置');
        const newConfig = useUserStore.getState().config;
        form.setFieldsValue(newConfig);
        setLocalGiftAnimations(newConfig.resources?.gift_animations || []);
      } else {
        message.error('恢复默认设置失败');
      }
    } catch (error) {
      message.error(`恢复默认设置失败: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleGiftAnimationChange = (giftName, animation) => {
    // 1. Update local state for immediate UI feedback
    const newAnimations = [...localGiftAnimations];
    const index = newAnimations.findIndex(item => item.name === giftName);
    
    if (index > -1) {
        if (animation) {
            newAnimations[index].animation = animation;
        } else {
            // Remove entry if cleared
            newAnimations.splice(index, 1);
        }
    } else {
        if (animation) {
            newAnimations.push({ name: giftName, animation });
        }
    }
    setLocalGiftAnimations(newAnimations);
    
    // 2. Sync to form values (so debouncedSave picks it up)
    // We construct the full resources object to pass to debouncedSave
    const currentValues = form.getFieldsValue(true);
    const newResources = {
        ...currentValues.resources,
        gift_animations: newAnimations
    };
    
    // Update form state but don't trigger validation
    form.setFieldValue(['resources', 'gift_animations'], newAnimations);

    // 3. Trigger save
    setSaving(true);
    debouncedSave({
        ...currentValues,
        resources: newResources
    });
  };

  const giftColumns = [
    { title: 'ID', dataIndex: 'id', width: 60, align: 'center' },
    { 
        title: '图标', 
        dataIndex: 'img', 
        width: 60, 
        align: 'center',
        render: (src) => src ? <img src={src} alt="" style={{width: 30, height: 30, objectFit: 'contain'}} /> : '-' 
    },
    { title: '名称', dataIndex: 'name', width: 120 },
    { 
        title: '价格 (元)', 
        dataIndex: 'price', 
        width: 80, 
        render: (price) => price ? `¥${price.toFixed(1)}` : '¥0.0' 
    },
    { 
        title: '动画素材', 
        key: 'animation',
        width: 200,
        render: (_, record) => {
            const mapping = localGiftAnimations.find(m => m.name === record.name);
            const value = mapping ? mapping.animation : undefined;
            return (
                <Select 
                  style={{ width: '100%' }} 
                  allowClear 
                  placeholder="选择动画"
                  value={value}
                  onChange={(val) => handleGiftAnimationChange(record.name, val)}
                  size="small"
                >
                    {assetList.map(asset => (
                        <Option key={asset} value={asset}>{asset}</Option>
                    ))}
                </Select>
            );
        }
    }
  ];

  const guardTypes = [
      { type: 'common', label: '白字' },
      { type: 'captain', label: '舰长' },
      { type: 'admiral', label: '提督' },
      { type: 'governor', label: '总督' }
  ];

  const guardColumns = [
      { title: '舰队类型', dataIndex: 'label', width: 100 },
      {
          title: '形象素材',
          key: 'skin',
          render: (_, record) => (
              <Form.Item 
                name={['resources', 'guard_skins', record.type]} 
                style={{ marginBottom: 0 }}
              >
                  <Select style={{ width: '100%' }} allowClear placeholder="选择形象" size="small">
                      {assetList.map(asset => (
                          <Option key={asset} value={asset}>{asset}</Option>
                      ))}
                  </Select>
              </Form.Item>
          )
      }
  ];

  const filteredGiftList = useMemo(() => {
      if (!searchText) return giftList;
      return giftList.filter(gift => 
          gift.name.toLowerCase().includes(searchText.toLowerCase())
      );
  }, [giftList, searchText]);

  return (
    <Drawer
      title={
        <Space>
          <span>设置</span>
          {saving && <Spin indicator={<LoadingOutlined style={{ fontSize: 16 }} spin />} />}
          {saving && <Text type="secondary" style={{ fontSize: 12 }}>保存中...</Text>}
        </Space>
      }
      placement="right"
      onClose={onClose}
      open={visible}
      width={600}
    >
      <Form 
        form={form} 
        layout="vertical"
        onValuesChange={handleValuesChange}
      >
        <Title level={5}>通用设置</Title>
        <Form.Item name={['system', 'auto_login']} valuePropName="checked" style={{ marginBottom: 8 }}>
          <Checkbox>自动登录账号</Checkbox>
        </Form.Item>
        <Form.Item name={['system', 'auto_connect']} valuePropName="checked">
          <Checkbox>自动连接房间</Checkbox>
        </Form.Item>

        <Divider />

        <Title level={5}>资源配置</Title>
        
        <Text strong>礼物 - 动画映射</Text>
        <Input 
            placeholder="搜索礼物名称" 
            value={searchText} 
            onChange={(e) => setSearchText(e.target.value)} 
            style={{ marginTop: 8, marginBottom: 8 }} 
            allowClear
        />
        <Table 
            dataSource={filteredGiftList} 
            columns={giftColumns} 
            rowKey="id" 
            size="small" 
            pagination={false} 
            scroll={{ y: 300 }}
            loading={loadingData}
            style={{ marginTop: 8 }}
            bordered
            showHeader={false}
        />

        <Divider style={{ margin: '12px 0' }} />

        <Text strong>舰队 - 形象映射</Text>
        <Table
            dataSource={guardTypes}
            columns={guardColumns}
            rowKey="type"
            size="small"
            pagination={false}
            style={{ marginTop: 8 }}
            bordered={false}
            showHeader={false}
        />

        <Divider />
        
        <Popconfirm
            title="恢复默认设置"
            description="确定要恢复默认设置吗？这将丢失当前的所有修改。"
            onConfirm={handleReset}
            okText="确定"
            cancelText="取消"
        >
            <Button type="dashed" icon={<ReloadOutlined />} block danger>恢复默认设置</Button>
        </Popconfirm>
      </Form>
    </Drawer>
  );
};

export default SettingsPanel;
