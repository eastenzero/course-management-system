import React, { useState } from 'react';
import { 
  Layout, 
  Row, 
  Col, 
  Card, 
  Space, 
  Typography, 
  Divider, 
  Button, 
  Switch,
  Tag,
  Badge,
  Avatar,
  Progress,
  Timeline,
  Tabs,
  Alert
} from 'antd';
import {
  AppstoreOutlined,
  SettingOutlined,
  EyeOutlined,
  ThunderboltOutlined,
  StarOutlined,
  TrophyOutlined,
  BookOutlined,
  UserOutlined
} from '@ant-design/icons';

import { useTheme } from '../../hooks/useThemeV2';
import { EnhancedGlassButton, EnhancedGlassCard, EnhancedGlassInput } from '../../components/glass';
import PerformanceMonitor from '../../components/common/PerformanceMonitor';
import './UIShowcase.css';

const { Header, Content } = Layout;
const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

const UIShowcase: React.FC = () => {
  const { 
    currentTheme, 
    setTheme, 
    monetThemes,
    morandiThemes,
    antdTheme
  } = useTheme();

  const [activeTab, setActiveTab] = useState('components');

  // 演示数据
  const demoStats = [
    { title: '今日课程', value: 4, color: '#52c41a' },
    { title: '待完成作业', value: 2, color: '#faad14' },
    { title: '本周测验', value: 1, color: '#1890ff' },
    { title: '平均分数', value: 87, color: '#722ed1' }
  ];

  const timelineData = [
    {
      children: '数学课 - 高等数学',
      color: 'blue',
      time: '09:00-10:30'
    },
    {
      children: '物理实验课',
      color: 'green',
      time: '14:00-16:00'
    },
    {
      children: '作业截止: 算法设计',
      color: 'red',
      time: '23:59'
    }
  ];

  return (
    <Layout className="ui-showcase">
      <Header className="showcase-header">
        <div className="header-content">
          <Title level={3} style={{ color: 'white', margin: 0 }}>
            <AppstoreOutlined /> UI 重设计演示
          </Title>
          
          <Space>
            <Text style={{ color: 'white' }}>主题:</Text>
            <Space.Compact>
              {Object.entries(monetThemes).map(([key, theme]) => (
                <Button
                  key={`monet-${key}`}
                  size="small"
                  type={currentTheme.includes(`monet-${key}`) ? 'primary' : 'default'}
                  onClick={() => setTheme(`monet-${key}`)}
                >
                  {theme.name}
                </Button>
              ))}
              {Object.entries(morandiThemes).map(([key, theme]) => (
                <Button
                  key={`morandi-${key}`}
                  size="small"
                  type={currentTheme.includes(`morandi-${key}`) ? 'primary' : 'default'}
                  onClick={() => setTheme(`morandi-${key}`)}
                >
                  {theme.name}
                </Button>
              ))}
            </Space.Compact>
          </Space>
        </div>
      </Header>

      <Content className="showcase-content">
        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          size="large"
          tabBarStyle={{ marginBottom: '24px' }}
        >
          <TabPane tab="组件展示" key="components">
            <Row gutter={[24, 24]}>
              {/* 玻璃按钮展示 */}
              <Col xs={24} lg={12}>
                <EnhancedGlassCard title="Enhanced Glass 按钮" glassLevel="md" borderGlow>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Space wrap>
                      <EnhancedGlassButton type="primary" glassLevel="sm">
                        小级别毛玻璃
                      </EnhancedGlassButton>
                      <EnhancedGlassButton type="primary" glassLevel="md" glow>
                        中级别 + 发光
                      </EnhancedGlassButton>
                      <EnhancedGlassButton type="primary" glassLevel="lg">
                        大级别毛玻璃
                      </EnhancedGlassButton>
                    </Space>
                    
                    <Space wrap>
                      <EnhancedGlassButton icon={<StarOutlined />}>
                        图标按钮
                      </EnhancedGlassButton>
                      <EnhancedGlassButton loading>
                        加载中
                      </EnhancedGlassButton>
                      <EnhancedGlassButton danger>
                        危险操作
                      </EnhancedGlassButton>
                    </Space>
                  </Space>
                </EnhancedGlassCard>
              </Col>

              {/* 玻璃卡片展示 */}
              <Col xs={24} lg={12}>
                <EnhancedGlassCard 
                  title="学习统计" 
                  glassLevel="lg" 
                  gradientBg
                  extra={<Badge count={3} />}
                >
                  <Row gutter={[16, 16]}>
                    {demoStats.map((stat, index) => (
                      <Col span={12} key={index}>
                        <div className="stat-item">
                          <Text type="secondary">{stat.title}</Text>
                          <Title level={3} style={{ color: stat.color, margin: 0 }}>
                            {stat.value}
                          </Title>
                        </div>
                      </Col>
                    ))}
                  </Row>
                </EnhancedGlassCard>
              </Col>

              {/* 玻璃输入框展示 */}
              <Col xs={24} lg={12}>
                <EnhancedGlassCard title="Enhanced Glass 输入组件" glassLevel="md">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <EnhancedGlassInput 
                      placeholder="标准玻璃输入框"
                      glassLevel="sm"
                    />
                    <EnhancedGlassInput 
                      placeholder="发光效果输入框"
                      glassLevel="md"
                    />
                    <EnhancedGlassInput 
                      placeholder="搜索课程..."
                      glassLevel="lg"
                      prefix={<BookOutlined />}
                    />
                  </Space>
                </EnhancedGlassCard>
              </Col>

              {/* 成就徽章展示 */}
              <Col xs={24} lg={12}>
                <EnhancedGlassCard title="成就系统" glassLevel="md" borderGlow>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div className="achievement-item">
                      <Avatar 
                        size={48} 
                        icon={<TrophyOutlined />} 
                        style={{ backgroundColor: '#faad14' }} 
                      />
                      <div className="achievement-content">
                        <Text strong>学霸达人</Text>
                        <br />
                        <Text type="secondary">连续7天完成所有作业</Text>
                      </div>
                      <Progress 
                        type="circle" 
                        size={40} 
                        percent={85} 
                        format={percent => `${percent}%`}
                      />
                    </div>
                    
                    <div className="achievement-item">
                      <Avatar 
                        size={48} 
                        icon={<StarOutlined />} 
                        style={{ backgroundColor: '#52c41a' }} 
                      />
                      <div className="achievement-content">
                        <Text strong>满分选手</Text>
                        <br />
                        <Text type="secondary">获得5次满分成绩</Text>
                      </div>
                      <Progress 
                        type="circle" 
                        size={40} 
                        percent={100} 
                        strokeColor="#52c41a"
                      />
                    </div>
                  </Space>
                </EnhancedGlassCard>
              </Col>

              {/* 今日课表 */}
              <Col xs={24}>
                <EnhancedGlassCard title="今日课表" glassLevel="lg" gradientBg>
                  <Timeline>
                    {timelineData.map((item, index) => (
                      <Timeline.Item color={item.color} key={index}>
                        <div className="timeline-item">
                          <Text strong>{item.children}</Text>
                          <Tag color={item.color} style={{ marginLeft: 'auto' }}>
                            {item.time}
                          </Tag>
                        </div>
                      </Timeline.Item>
                    ))}
                  </Timeline>
                </EnhancedGlassCard>
              </Col>
            </Row>
          </TabPane>

          <TabPane tab="性能监控" key="performance">
            <Row>
              <Col span={24}>
                <Alert
                  message="性能与无障碍监控"
                  description="实时监控应用性能指标和无障碍功能状态"
                  type="info"
                  showIcon
                  style={{ marginBottom: '24px' }}
                />
                <PerformanceMonitor />
              </Col>
            </Row>
          </TabPane>

          <TabPane tab="主题预览" key="themes">
            <Row gutter={[24, 24]}>
              <Col span={24}>
                <Alert
                  message="Design Tokens 主题系统"
                  description="基于莫奈印象派和莫兰迪色彩美学的主题系统，支持深色模式切换"
                  type="info"
                  showIcon
                  style={{ marginBottom: '24px' }}
                />
              </Col>
              
              <Col xs={24} lg={12}>
                <Card title="莫奈印象派系列">
                  <Row gutter={[16, 16]}>
                    {Object.entries(monetThemes).map(([key, theme]) => (
                      <Col span={24} key={key}>
                        <div 
                          className="theme-preview"
                          onClick={() => setTheme(`monet-${key}`)}
                          style={{ 
                            cursor: 'pointer',
                            border: currentTheme.includes(`monet-${key}`) ? '2px solid #1890ff' : '1px solid #d9d9d9'
                          }}
                        >
                          <div className="theme-colors">
                            <div 
                              className="color-swatch primary" 
                              style={{ backgroundColor: theme.primary }}
                            />
                            <div 
                              className="color-swatch secondary" 
                              style={{ backgroundColor: theme.secondary }}
                            />
                            <div 
                              className="color-swatch accent" 
                              style={{ backgroundColor: theme.accent }}
                            />
                          </div>
                          <div className="theme-info">
                            <Text strong>{theme.name}</Text>
                            <br />
                            <Text type="secondary">Key: {key}</Text>
                          </div>
                        </div>
                      </Col>
                    ))}
                  </Row>
                </Card>
              </Col>
              
              <Col xs={24} lg={12}>
                <Card title="莫兰迪色彩系列">
                  <Row gutter={[16, 16]}>
                    {Object.entries(morandiThemes).map(([key, theme]) => (
                      <Col span={24} key={key}>
                        <div 
                          className="theme-preview"
                          onClick={() => setTheme(`morandi-${key}`)}
                          style={{ 
                            cursor: 'pointer',
                            border: currentTheme.includes(`morandi-${key}`) ? '2px solid #1890ff' : '1px solid #d9d9d9'
                          }}
                        >
                          <div className="theme-colors">
                            <div 
                              className="color-swatch primary" 
                              style={{ backgroundColor: theme.primary }}
                            />
                            <div 
                              className="color-swatch secondary" 
                              style={{ backgroundColor: theme.secondary }}
                            />
                            <div 
                              className="color-swatch accent" 
                              style={{ backgroundColor: theme.accent }}
                            />
                          </div>
                          <div className="theme-info">
                            <Text strong>{theme.name}</Text>
                            <br />
                            <Text type="secondary">Key: {key}</Text>
                          </div>
                        </div>
                      </Col>
                    ))}
                  </Row>
                </Card>
              </Col>
            </Row>
          </TabPane>

          <TabPane tab="无障碍功能" key="accessibility">
            <Row gutter={[24, 24]}>
              <Col span={24}>
                <Alert
                  message="无障碍功能说明"
                  description="本系统已实现WCAG AA级别的无障碍支持，包括键盘导航、屏幕阅读器支持、高对比度模式等"
                  type="success"
                  showIcon
                  style={{ marginBottom: '24px' }}
                />
              </Col>
              
              <Col xs={24} lg={8}>
                <Card title="🎹 键盘导航" size="small">
                  <Space direction="vertical">
                    <Text>• Tab - 切换焦点</Text>
                    <Text>• Enter/Space - 激活按钮</Text>
                    <Text>• Esc - 关闭弹窗</Text>
                    <Text>• 方向键 - 菜单导航</Text>
                  </Space>
                </Card>
              </Col>
              
              <Col xs={24} lg={8}>
                <Card title="👁️ 视觉优化" size="small">
                  <Space direction="vertical">
                    <Text>• 高对比度色彩</Text>
                    <Text>• 可调节字体大小</Text>
                    <Text>• 减少动效模式</Text>
                    <Text>• 焦点清晰指示</Text>
                  </Space>
                </Card>
              </Col>
              
              <Col xs={24} lg={8}>
                <Card title="📱 兼容性" size="small">
                  <Space direction="vertical">
                    <Text>• 屏幕阅读器支持</Text>
                    <Text>• 语义化HTML</Text>
                    <Text>• ARIA标签完整</Text>
                    <Text>• 多设备适配</Text>
                  </Space>
                </Card>
              </Col>
            </Row>
          </TabPane>
        </Tabs>
      </Content>
    </Layout>
  );
};

export default UIShowcase;