import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  Form,
  Switch,
  Select,
  Button,
  message,
  Space,
  Divider,
  Row,
  Col,
  Alert,
  Radio,
  Slider,
} from 'antd';
import {
  SettingOutlined,
  BellOutlined,
  EyeOutlined,
  GlobalOutlined,
  SaveOutlined,
  MoonOutlined,
  SunOutlined,
} from '@ant-design/icons';
import { notificationAPI, userAPI } from '../../services/api';

const { Title } = Typography;
const { Option } = Select;

interface UserSettings {
  // 通知设置
  emailNotifications: boolean;
  smsNotifications: boolean;
  systemNotifications: boolean;
  courseReminders: boolean;
  
  // 显示设置
  theme: 'light' | 'dark' | 'auto';
  language: 'zh-CN' | 'en-US';
  pageSize: number;
  dateFormat: string;
  
  // 隐私设置
  profileVisibility: 'public' | 'private' | 'friends';
  showEmail: boolean;
  showPhone: boolean;
  
  // 系统设置
  autoLogout: number; // 分钟
  sessionTimeout: boolean;
}

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);

        // 获取通知偏好设置
        const notificationResponse = await notificationAPI.getPreferences();
        const notificationPrefs = notificationResponse.data;

        // 获取用户偏好设置
        const preferenceResponse = await userAPI.getPreferences();
        const userPrefs = preferenceResponse.data;

        // 构建用户设置对象
        const userSettings: UserSettings = {
          emailNotifications: notificationPrefs.enable_email_notifications || false,
          smsNotifications: false, // 短信通知暂时不支持
          systemNotifications: notificationPrefs.enable_websocket_notifications || true,
          courseReminders: notificationPrefs.course_enrollment_channels?.includes('websocket') || true,
          theme: userPrefs.theme || 'light',
          language: userPrefs.language || 'zh-CN',
          pageSize: userPrefs.page_size || 10,
          dateFormat: userPrefs.date_format || 'YYYY-MM-DD',
          profileVisibility: userPrefs.profile_visibility || 'public',
          showEmail: userPrefs.show_email !== undefined ? userPrefs.show_email : true,
          showPhone: userPrefs.show_phone !== undefined ? userPrefs.show_phone : false,
          autoLogout: userPrefs.auto_logout || 30,
          sessionTimeout: userPrefs.session_timeout !== undefined ? userPrefs.session_timeout : true,
        };

        setSettings(userSettings);
        form.setFieldsValue(userSettings);
      } catch (error) {
        console.error('获取设置失败:', error);
        message.error('获取设置失败，请检查网络连接或联系管理员');
        
        // 使用默认设置
        const defaultSettings: UserSettings = {
          emailNotifications: true,
          smsNotifications: false,
          systemNotifications: true,
          courseReminders: true,
          theme: 'light',
          language: 'zh-CN',
          pageSize: 10,
          dateFormat: 'YYYY-MM-DD',
          profileVisibility: 'public',
          showEmail: true,
          showPhone: false,
          autoLogout: 30,
          sessionTimeout: true,
        };

        setSettings(defaultSettings);
        form.setFieldsValue(defaultSettings);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, [form]);

  const handleSubmit = async (values: UserSettings) => {
    try {
      setSubmitting(true);

      // 保存通知偏好设置
      const notificationPrefs = {
        enable_email_notifications: values.emailNotifications,
        enable_websocket_notifications: values.systemNotifications,
        course_enrollment_channels: values.courseReminders ? ['websocket'] : [],
        grade_published_channels: values.emailNotifications ? ['websocket', 'email'] : ['websocket'],
        assignment_due_channels: values.systemNotifications ? ['websocket'] : [],
        schedule_change_channels: values.emailNotifications ? ['websocket', 'email'] : ['websocket'],
        system_announcement_channels: values.systemNotifications ? ['websocket'] : [],
      };

      await notificationAPI.updatePreferences(notificationPrefs);

      // 保存用户偏好设置
      const userPrefs = {
        theme: values.theme,
        language: values.language,
        page_size: values.pageSize,
        date_format: values.dateFormat,
        profile_visibility: values.profileVisibility,
        show_email: values.showEmail,
        show_phone: values.showPhone,
        auto_logout: values.autoLogout,
        session_timeout: values.sessionTimeout,
      };

      await userAPI.updatePreferences(userPrefs);

      setSettings(values);
      message.success('设置保存成功');
    } catch (error) {
      console.error('保存设置失败:', error);
      message.error('保存失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    if (settings) {
      form.setFieldsValue(settings);
      message.info('已重置为上次保存的设置');
    }
  };

  if (loading || !settings) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div>加载中...</div>
      </div>
    );
  }

  return (
    <div className="settings-page">
      <div className="page-header">
        <Title level={2}>系统设置</Title>
        <p>个性化配置您的使用体验</p>
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={settings}
      >
        <Row gutter={24}>
          <Col xs={24} lg={12}>
            {/* 通知设置 */}
            <Card 
              title={
                <Space>
                  <BellOutlined />
                  <span>通知设置</span>
                </Space>
              }
              size="small"
              style={{ marginBottom: '16px' }}
            >
              <Form.Item
                name="emailNotifications"
                label="邮件通知"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="smsNotifications"
                label="短信通知"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="systemNotifications"
                label="系统通知"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="courseReminders"
                label="课程提醒"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Card>

            {/* 显示设置 */}
            <Card 
              title={
                <Space>
                  <EyeOutlined />
                  <span>显示设置</span>
                </Space>
              }
              size="small"
            >
              <Form.Item
                name="theme"
                label="主题模式"
              >
                <Radio.Group>
                  <Radio.Button value="light">
                    <SunOutlined /> 浅色
                  </Radio.Button>
                  <Radio.Button value="dark">
                    <MoonOutlined /> 深色
                  </Radio.Button>
                  <Radio.Button value="auto">
                    <SettingOutlined /> 自动
                  </Radio.Button>
                </Radio.Group>
              </Form.Item>

              <Form.Item
                name="language"
                label="语言"
              >
                <Select>
                  <Option value="zh-CN">简体中文</Option>
                  <Option value="en-US">English</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="pageSize"
                label="每页显示条数"
              >
                <Select>
                  <Option value={10}>10条</Option>
                  <Option value={20}>20条</Option>
                  <Option value={50}>50条</Option>
                  <Option value={100}>100条</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="dateFormat"
                label="日期格式"
              >
                <Select>
                  <Option value="YYYY-MM-DD">2024-08-14</Option>
                  <Option value="YYYY/MM/DD">2024/08/14</Option>
                  <Option value="DD/MM/YYYY">14/08/2024</Option>
                  <Option value="MM/DD/YYYY">08/14/2024</Option>
                </Select>
              </Form.Item>
            </Card>
          </Col>

          <Col xs={24} lg={12}>
            {/* 隐私设置 */}
            <Card 
              title={
                <Space>
                  <GlobalOutlined />
                  <span>隐私设置</span>
                </Space>
              }
              size="small"
              style={{ marginBottom: '16px' }}
            >
              <Form.Item
                name="profileVisibility"
                label="个人资料可见性"
              >
                <Radio.Group>
                  <Radio value="public">公开</Radio>
                  <Radio value="friends">仅好友</Radio>
                  <Radio value="private">私密</Radio>
                </Radio.Group>
              </Form.Item>

              <Form.Item
                name="showEmail"
                label="显示邮箱地址"
                valuePropName="checked"
              >
                <Switch checkedChildren="显示" unCheckedChildren="隐藏" />
              </Form.Item>

              <Form.Item
                name="showPhone"
                label="显示手机号码"
                valuePropName="checked"
              >
                <Switch checkedChildren="显示" unCheckedChildren="隐藏" />
              </Form.Item>
            </Card>

            {/* 安全设置 */}
            <Card 
              title={
                <Space>
                  <SettingOutlined />
                  <span>安全设置</span>
                </Space>
              }
              size="small"
            >
              <Form.Item
                name="sessionTimeout"
                label="会话超时保护"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="autoLogout"
                label="自动登出时间（分钟）"
              >
                <Slider
                  min={5}
                  max={120}
                  step={5}
                  marks={{
                    5: '5分钟',
                    30: '30分钟',
                    60: '1小时',
                    120: '2小时',
                  }}
                />
              </Form.Item>

              <Alert
                message="安全提示"
                description="启用会话超时保护可以在您长时间未操作时自动登出，保护账户安全。"
                type="info"
                showIcon
                style={{ marginTop: '16px' }}
              />
            </Card>
          </Col>
        </Row>

        <Divider />

        <div style={{ textAlign: 'center' }}>
          <Space size="large">
            <Button onClick={handleReset}>
              重置
            </Button>
            <Button 
              type="primary" 
              htmlType="submit"
              loading={submitting}
              icon={<SaveOutlined />}
              size="large"
            >
              保存设置
            </Button>
          </Space>
        </div>
      </Form>
    </div>
  );
};

export default SettingsPage;
