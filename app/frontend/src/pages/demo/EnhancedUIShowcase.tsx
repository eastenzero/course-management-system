import React, { useState } from 'react';
import { 
  Row, 
  Col, 
  Typography, 
  Space, 
  Divider, 
  Form, 
  Input,
  Select, 
  Switch,
  Button,
  Card,
  message,
  Table,
  Tag,
  Progress,
  Alert
} from 'antd';
import { 
  SearchOutlined, 
  UserOutlined, 
  LockOutlined,
  SendOutlined,
  HeartOutlined,
  StarOutlined,
  SettingOutlined,
  PlusOutlined
} from '@ant-design/icons';
import { useTheme } from '../hooks/useThemeV2';
import EnhancedThemeSelector from '../components/common/EnhancedThemeSelector';
import './EnhancedUIShowcase.css';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

const EnhancedUIShowcase: React.FC = () => {
  const { uiTheme, setUITheme, toggleMode, getThemeColors, userRole } = useTheme();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const values = await form.validateFields();
      message.success('表单提交成功！');
      console.log('Form values:', values);
    } catch (error) {
      message.error('请检查表单输入');
    } finally {
      setTimeout(() => setLoading(false), 1000);
    }
  };

  const themeColors = getThemeColors();

  // 表格数据
  const tableData = [
    {
      key: '1',
      name: '高等数学A',
      teacher: '张教授',
      students: 120,
      progress: 75,
      status: '进行中',
    },
    {
      key: '2',
      name: '大学物理',
      teacher: '李老师',
      students: 85,
      progress: 90,
      status: '已完成',
    },
    {
      key: '3',
      name: '程序设计基础',
      teacher: '王老师',
      students: 95,
      progress: 60,
      status: '进行中',
    },
  ];

  const tableColumns = [
    {
      title: '课程名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: '授课教师',
      dataIndex: 'teacher',
      key: 'teacher',
    },
    {
      title: '学生人数',
      dataIndex: 'students',
      key: 'students',
      render: (count: number) => <Text type="secondary">{count}人</Text>,
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number) => (
        <Progress 
          percent={progress} 
          size="small" 
          strokeColor={themeColors?.primary}
        />
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === '已完成' ? 'success' : 'processing'}>
          {status}
        </Tag>
      ),
    },
  ];

  return (
    <div className="enhanced-ui-showcase">
      {/* 页面头部 */}
      <div className="showcase-header glass-surface">
        <div className="header-content">
          <div>
            <Title level={1} style={{ margin: 0, color: themeColors?.primary }}>
              UI 重设计展示
            </Title>
            <Paragraph style={{ margin: '8px 0 0', color: 'var(--neutral-text-secondary)' }}>
              基于莫奈/莫兰迪美学的玻璃拟态设计系统 - {themeColors?.name}
            </Paragraph>
          </div>
          <EnhancedThemeSelector />
        </div>
      </div>

      <div className="showcase-content">
        <Row gutter={[24, 24]}>
          {/* 主题信息卡片 */}
          <Col span={24}>
            <Card 
              className="glass-surface-secondary"
              title={
                <Space>
                  <SettingOutlined />
                  <span>当前主题信息</span>
                </Space>
              }
            >
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={8}>
                  <div className="theme-info-item">
                    <Text type="secondary">主题类别</Text>
                    <br />
                    <Text strong>
                      {uiTheme.category === 'monet' ? '莫奈系列' : '莫兰迪系列'}
                    </Text>
                  </div>
                </Col>
                <Col xs={24} sm={8}>
                  <div className="theme-info-item">
                    <Text type="secondary">主题名称</Text>
                    <br />
                    <Text strong>{themeColors?.name}</Text>
                  </div>
                </Col>
                <Col xs={24} sm={8}>
                  <div className="theme-info-item">
                    <Text type="secondary">显示模式</Text>
                    <br />
                    <Space>
                      <Text strong>
                        {uiTheme.mode === 'dark' ? '深色模式' : '浅色模式'}
                      </Text>
                      <Switch
                        size="small"
                        checked={uiTheme.mode === 'dark'}
                        onChange={toggleMode}
                      />
                    </Space>
                  </div>
                </Col>
              </Row>
              
              {/* 色彩展示 */}
              <Divider />
              <div className="color-palette-section">
                <Text strong>主题色彩：</Text>
                <div className="color-palette">
                  <div className="color-item">
                    <div 
                      className="color-circle" 
                      style={{ backgroundColor: themeColors?.primary }}
                    />
                    <Text>主色</Text>
                  </div>
                  <div className="color-item">
                    <div 
                      className="color-circle" 
                      style={{ backgroundColor: themeColors?.secondary }}
                    />
                    <Text>辅色</Text>
                  </div>
                  <div className="color-item">
                    <div 
                      className="color-circle" 
                      style={{ backgroundColor: themeColors?.tertiary }}
                    />
                    <Text>点缀</Text>
                  </div>
                  <div className="color-item">
                    <div 
                      className="color-circle" 
                      style={{ backgroundColor: themeColors?.accent }}
                    />
                    <Text>强调</Text>
                  </div>
                </div>
              </div>
            </Card>
          </Col>

          {/* 表单组件展示 */}
          <Col xs={24} lg={12}>
            <Card 
              className="glass-surface"
              title="表单组件展示"
            >
              <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
              >
                <Form.Item
                  label="用户名"
                  name="username"
                  rules={[{ required: true, message: '请输入用户名' }]}
                >
                  <Input 
                    prefix={<UserOutlined />} 
                    placeholder="输入用户名" 
                  />
                </Form.Item>

                <Form.Item
                  label="密码"
                  name="password"
                  rules={[{ required: true, message: '请输入密码' }]}
                >
                  <Input.Password 
                    prefix={<LockOutlined />} 
                    placeholder="输入密码" 
                  />
                </Form.Item>

                <Form.Item
                  label="角色选择"
                  name="role"
                >
                  <Select placeholder="选择角色" allowClear>
                    <Option value="teacher">教师</Option>
                    <Option value="student">学生</Option>
                    <Option value="admin">管理员</Option>
                  </Select>
                </Form.Item>

                <Form.Item>
                  <Space>
                    <Button 
                      type="primary" 
                      htmlType="submit" 
                      loading={loading}
                      icon={<SendOutlined />}
                    >
                      提交
                    </Button>
                    <Button icon={<PlusOutlined />}>
                      新建
                    </Button>
                    <Button 
                      type="dashed" 
                      onClick={() => form.resetFields()}
                    >
                      重置
                    </Button>
                  </Space>
                </Form.Item>
              </Form>
            </Card>
          </Col>

          {/* 数据展示 */}
          <Col xs={24} lg={12}>
            <Card 
              className="glass-surface"
              title="数据展示"
            >
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                <Alert
                  message="系统提示"
                  description="这是一个基于新Design Tokens系统的UI展示页面。"
                  type="info"
                  showIcon
                  closable
                />

                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-number" style={{ color: themeColors?.primary }}>
                      1,234
                    </div>
                    <div className="stat-label">总用户</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-number" style={{ color: themeColors?.secondary }}>
                      89
                    </div>
                    <div className="stat-label">在线用户</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-number" style={{ color: themeColors?.accent }}>
                      567
                    </div>
                    <div className="stat-label">今日访问</div>
                  </div>
                </div>

                <div>
                  <Text strong>快速操作：</Text>
                  <br />
                  <Space wrap style={{ marginTop: '8px' }}>
                    <Button size="small" type="primary" ghost icon={<HeartOutlined />}>
                      收藏
                    </Button>
                    <Button size="small" icon={<StarOutlined />}>
                      评分
                    </Button>
                    <Button size="small" type="dashed">
                      分享
                    </Button>
                  </Space>
                </div>
              </Space>
            </Card>
          </Col>

          {/* 表格展示 */}
          <Col span={24}>
            <Card 
              className="glass-surface"
              title="表格展示"
            >
              <Table
                columns={tableColumns}
                dataSource={tableData}
                pagination={false}
                size="middle"
              />
            </Card>
          </Col>

          {/* 主题切换面板 */}
          <Col span={24}>
            <Card 
              className="glass-surface-tertiary"
              title="主题切换演示"
            >
              <Row gutter={[24, 16]}>
                <Col xs={24} sm={8}>
                  <div>
                    <Text strong>主题类别：</Text>
                    <br />
                    <Select
                      value={uiTheme.category}
                      onChange={(category) => setUITheme(category, uiTheme.themeKey)}
                      style={{ width: '100%', marginTop: 8 }}
                    >
                      <Option value="monet">莫奈系列</Option>
                      <Option value="morandi">莫兰迪系列</Option>
                    </Select>
                  </div>
                </Col>
                
                <Col xs={24} sm={8}>
                  <div>
                    <Text strong>主题变体：</Text>
                    <br />
                    <Select
                      value={uiTheme.themeKey}
                      onChange={(themeKey) => setUITheme(uiTheme.category, themeKey)}
                      style={{ width: '100%', marginTop: 8 }}
                    >
                      <Option value="a">
                        {uiTheme.category === 'monet' ? '清晨湖畔' : '岩石与苔'}
                      </Option>
                      <Option value="b">
                        {uiTheme.category === 'monet' ? '晨光花园' : '燕麦与石墨'}
                      </Option>
                      <Option value="c">
                        {uiTheme.category === 'monet' ? '海风与薰衣' : '陶瓷与烟灰'}
                      </Option>
                    </Select>
                  </div>
                </Col>

                <Col xs={24} sm={8}>
                  <div>
                    <Text strong>用户角色：</Text>
                    <br />
                    <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
                      {userRole === 'teacher' && '教师端 - 推荐莫兰迪主题'}
                      {userRole === 'student' && '学生端 - 推荐莫奈主题'}
                      {!userRole && '未设置角色'}
                    </Text>
                  </div>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default EnhancedUIShowcase;