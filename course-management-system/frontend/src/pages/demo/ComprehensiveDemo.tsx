import React, { useState } from 'react';
import { 
  Row, 
  Col, 
  Typography, 
  Space, 
  Divider, 
  Form, 
  Select, 
  Switch,
  message,
  Table,
  Tag,
  Progress,
  Alert,
  Tabs
} from 'antd';
import { 
  UserOutlined, 
  LockOutlined,
  SendOutlined,
  PlusOutlined,
  StarOutlined,
  HeartOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useTheme } from '../../hooks/useThemeV2';
import { 
  EnhancedGlassButton, 
  EnhancedGlassCard, 
  EnhancedGlassInput 
} from '../../components/glass';
import EnhancedThemeSelector from '../../components/common/EnhancedThemeSelector';
import './ComprehensiveDemo.css';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const ComprehensiveDemo: React.FC = () => {
  const { uiTheme, getThemeColors } = useTheme();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const themeColors = getThemeColors();

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const values = await form.validateFields();
      message.success('表单提交成功！');
    } catch (error) {
      message.error('请检查表单输入');
    } finally {
      setTimeout(() => setLoading(false), 1000);
    }
  };

  return (
    <div className="comprehensive-demo">
      {/* 页面头部 */}
      <div className="demo-header glass-surface">
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={1} style={{ margin: 0 }}>
              UI重设计系统演示
            </Title>
            <Text type="secondary">
              基于莫奈/莫兰迪美学的现代化UI系统
            </Text>
          </Col>
          <Col>
            <EnhancedThemeSelector />
          </Col>
        </Row>
      </div>

      <div className="demo-content">
        <Tabs defaultActiveKey="1">
          <TabPane tab="组件展示" key="1">
            <Row gutter={[24, 24]}>
              {/* 按钮组件展示 */}
              <Col span={24}>
                <EnhancedGlassCard title="增强玻璃按钮" glassLevel="md">
                  <Space wrap size="middle">
                    <EnhancedGlassButton type="primary" icon={<SendOutlined />}>
                      主要按钮
                    </EnhancedGlassButton>
                    <EnhancedGlassButton icon={<PlusOutlined />}>
                      默认按钮
                    </EnhancedGlassButton>
                    <EnhancedGlassButton type="dashed" glow>
                      发光按钮
                    </EnhancedGlassButton>
                    <EnhancedGlassButton 
                      type="primary" 
                      loading={loading}
                      onClick={handleSubmit}
                    >
                      加载按钮
                    </EnhancedGlassButton>
                    <EnhancedGlassButton type="text" icon={<HeartOutlined />}>
                      文本按钮
                    </EnhancedGlassButton>
                  </Space>
                </EnhancedGlassCard>
              </Col>

              {/* 输入框展示 */}
              <Col xs={24} lg={12}>
                <EnhancedGlassCard title="增强玻璃输入框" glassLevel="lg">
                  <Form form={form} layout="vertical">
                    <Form.Item label="用户名" name="username">
                      <EnhancedGlassInput 
                        prefix={<UserOutlined />}
                        placeholder="请输入用户名"
                        glassLevel="md"
                        focusGlow
                      />
                    </Form.Item>
                    <Form.Item label="密码" name="password">
                      <EnhancedGlassInput.Password 
                        prefix={<LockOutlined />}
                        placeholder="请输入密码"
                        glassLevel="md"
                      />
                    </Form.Item>
                    <Form.Item label="角色" name="role">
                      <Select 
                        placeholder="选择角色" 
                        className="enhanced-glass-select"
                      >
                        <Option value="teacher">教师</Option>
                        <Option value="student">学生</Option>
                        <Option value="admin">管理员</Option>
                      </Select>
                    </Form.Item>
                  </Form>
                </EnhancedGlassCard>
              </Col>

              {/* 卡片展示 */}
              <Col xs={24} lg={12}>
                <EnhancedGlassCard 
                  title="玻璃卡片样式" 
                  glassLevel="sm"
                  borderGlow
                  extra={<SettingOutlined />}
                >
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Alert
                      message="主题信息"
                      description={`当前主题：${themeColors?.name}`}
                      type="info"
                      showIcon
                    />
                    <div>
                      <Text strong>主要特性：</Text>
                      <ul>
                        <li>毛玻璃背景效果</li>
                        <li>自适应明暗模式</li>
                        <li>平滑过渡动画</li>
                        <li>响应式设计</li>
                      </ul>
                    </div>
                  </Space>
                </EnhancedGlassCard>
              </Col>
            </Row>
          </TabPane>

          <TabPane tab="主题展示" key="2">
            <Row gutter={[24, 24]}>
              <Col span={24}>
                <EnhancedGlassCard title="主题色彩展示" gradientBg>
                  <div className="color-showcase">
                    <div className="color-item">
                      <div 
                        className="color-swatch large" 
                        style={{ backgroundColor: themeColors?.primary }}
                      />
                      <Text>主色</Text>
                      <Text type="secondary">{themeColors?.primary}</Text>
                    </div>
                    <div className="color-item">
                      <div 
                        className="color-swatch large" 
                        style={{ backgroundColor: themeColors?.secondary }}
                      />
                      <Text>辅色</Text>
                      <Text type="secondary">{themeColors?.secondary}</Text>
                    </div>
                    <div className="color-item">
                      <div 
                        className="color-swatch large" 
                        style={{ backgroundColor: themeColors?.tertiary }}
                      />
                      <Text>点缀色</Text>
                      <Text type="secondary">{themeColors?.tertiary}</Text>
                    </div>
                    <div className="color-item">
                      <div 
                        className="color-swatch large" 
                        style={{ backgroundColor: themeColors?.accent }}
                      />
                      <Text>强调色</Text>
                      <Text type="secondary">{themeColors?.accent}</Text>
                    </div>
                  </div>
                </EnhancedGlassCard>
              </Col>
            </Row>
          </TabPane>

          <TabPane tab="数据展示" key="3">
            <Row gutter={[24, 24]}>
              <Col span={24}>
                <EnhancedGlassCard title="数据表格" hoverable>
                  <Table
                    dataSource={[
                      { key: 1, name: '高等数学', teacher: '张教授', progress: 75 },
                      { key: 2, name: '大学物理', teacher: '李老师', progress: 90 },
                      { key: 3, name: '程序设计', teacher: '王老师', progress: 60 },
                    ]}
                    columns={[
                      { title: '课程名称', dataIndex: 'name', key: 'name' },
                      { title: '教师', dataIndex: 'teacher', key: 'teacher' },
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
                        )
                      },
                    ]}
                    pagination={false}
                  />
                </EnhancedGlassCard>
              </Col>
            </Row>
          </TabPane>
        </Tabs>
      </div>
    </div>
  );
};

export default ComprehensiveDemo;