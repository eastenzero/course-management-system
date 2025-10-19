import React from 'react';
import { Row, Col, Statistic, Button, Avatar, Progress } from 'antd';
import { 
  BookOutlined, 
  TrophyOutlined, 
  ClockCircleOutlined,
  UserOutlined,
  BellOutlined,
  CalendarOutlined,
  TeamOutlined,
  StarOutlined
} from '@ant-design/icons';
import { GlassCard } from '../../components/glass/GlassCard';
import { DynamicBackground } from '../../components/common/DynamicBackground';
import '../../styles/glass-theme.css';
import '../../styles/glass-animations.css';

const GlassEffectDemo: React.FC = () => {
  return (
    <div className="glass-page-background">
      {/* 动态背景 */}
      <DynamicBackground 
        density={0.08} 
        speed={0.8} 
        lineMaxDist={120} 
        triMaxDist={80}
      />
      
      <div className="glass-content">
        {/* 欢迎横幅 */}
        <GlassCard variant="primary" className="glass-welcome-banner glass-animate-slide-in">
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <Avatar size={64} icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
            <div style={{ flex: 1 }}>
              <h1 style={{ color: 'white', margin: 0, fontSize: '28px', fontWeight: 'bold' }}>
                毛玻璃效果演示
              </h1>
              <p style={{ color: 'rgba(255, 255, 255, 0.8)', margin: '8px 0 0 0', fontSize: '16px' }}>
                现代化的毛玻璃界面设计展示
              </p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>
                100%
              </div>
              <div style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>
                完成度
              </div>
            </div>
          </div>
        </GlassCard>

        {/* 统计卡片 */}
        <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} lg={6}>
            <GlassCard variant="primary" hoverable className="glass-animate-slide-in glass-animate-delay-1">
              <div className="glass-stat-card">
                <Statistic
                  title="学生界面"
                  value="已完成"
                  prefix={<BookOutlined style={{ color: '#1890ff' }} />}
                  valueStyle={{ color: 'white', fontWeight: 'bold', fontSize: '16px' }}
                />
              </div>
            </GlassCard>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <GlassCard variant="secondary" hoverable className="glass-animate-slide-in glass-animate-delay-2">
              <div className="glass-stat-card">
                <Statistic
                  title="教师界面"
                  value="已完成"
                  prefix={<CalendarOutlined style={{ color: '#52c41a' }} />}
                  valueStyle={{ color: 'white', fontWeight: 'bold', fontSize: '16px' }}
                />
              </div>
            </GlassCard>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <GlassCard variant="accent" hoverable className="glass-animate-slide-in glass-animate-delay-3">
              <div className="glass-stat-card">
                <Statistic
                  title="毛玻璃组件"
                  value="已完成"
                  prefix={<TrophyOutlined style={{ color: '#faad14' }} />}
                  valueStyle={{ color: 'white', fontWeight: 'bold', fontSize: '16px' }}
                />
              </div>
            </GlassCard>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <GlassCard variant="primary" hoverable className="glass-animate-slide-in glass-animate-delay-4">
              <div className="glass-stat-card">
                <Statistic
                  title="响应式设计"
                  value="已完成"
                  prefix={<StarOutlined style={{ color: '#722ed1' }} />}
                  valueStyle={{ color: 'white', fontWeight: 'bold', fontSize: '16px' }}
                />
              </div>
            </GlassCard>
          </Col>
        </Row>

        {/* 主要内容区域 */}
        <Row gutter={[24, 24]}>
          {/* 改造完成的页面 */}
          <Col xs={24} lg={14}>
            <GlassCard 
              title="已完成的页面改造" 
              variant="primary"
              className="glass-animate-slide-in-left"
              extra={<BellOutlined style={{ color: 'white' }} />}
            >
              <div style={{ display: 'grid', gap: '16px' }}>
                <div style={{
                  padding: '16px',
                  background: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.2)'
                }}>
                  <h4 style={{ color: 'white', margin: '0 0 8px 0' }}>学生仪表板</h4>
                  <p style={{ color: 'rgba(255, 255, 255, 0.7)', margin: 0, fontSize: '14px' }}>
                    完整的毛玻璃效果，包括欢迎横幅、统计卡片、快速操作和学习进度
                  </p>
                </div>
                <div style={{
                  padding: '16px',
                  background: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.2)'
                }}>
                  <h4 style={{ color: 'white', margin: '0 0 8px 0' }}>学生课程页面</h4>
                  <p style={{ color: 'rgba(255, 255, 255, 0.7)', margin: 0, fontSize: '14px' }}>
                    课程列表采用毛玻璃卡片设计，统计概览和详情模态框
                  </p>
                </div>
                <div style={{
                  padding: '16px',
                  background: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.2)'
                }}>
                  <h4 style={{ color: 'white', margin: '0 0 8px 0' }}>教师仪表板</h4>
                  <p style={{ color: 'rgba(255, 255, 255, 0.7)', margin: 0, fontSize: '14px' }}>
                    教师专用界面，包含教学统计和课程管理功能
                  </p>
                </div>
                <div style={{
                  padding: '16px',
                  background: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.2)'
                }}>
                  <h4 style={{ color: 'white', margin: '0 0 8px 0' }}>教师课程管理</h4>
                  <p style={{ color: 'rgba(255, 255, 255, 0.7)', margin: 0, fontSize: '14px' }}>
                    课程管理界面，包含学生管理、成绩录入等功能
                  </p>
                </div>
              </div>
            </GlassCard>
          </Col>

          {/* 技术特性 */}
          <Col xs={24} lg={10}>
            <GlassCard 
              title="技术特性" 
              variant="secondary"
              className="glass-animate-slide-in-right"
              extra={<StarOutlined style={{ color: 'white' }} />}
            >
              <div style={{ padding: '16px 0' }}>
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ color: 'white', fontSize: '14px' }}>毛玻璃效果</span>
                    <span style={{ color: 'white', fontSize: '14px' }}>100%</span>
                  </div>
                  <Progress 
                    percent={100}
                    strokeColor={{
                      '0%': '#1890ff',
                      '100%': '#40a9ff',
                    }}
                    trailColor="rgba(255, 255, 255, 0.2)"
                    strokeWidth={8}
                    showInfo={false}
                  />
                </div>
                
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ color: 'white', fontSize: '14px' }}>响应式设计</span>
                    <span style={{ color: 'white', fontSize: '14px' }}>100%</span>
                  </div>
                  <Progress 
                    percent={100}
                    strokeColor={{
                      '0%': '#52c41a',
                      '100%': '#73d13d',
                    }}
                    trailColor="rgba(255, 255, 255, 0.2)"
                    strokeWidth={8}
                    showInfo={false}
                  />
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
                      4
                    </div>
                    <div style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '12px' }}>
                      页面改造
                    </div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
                      3
                    </div>
                    <div style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '12px' }}>
                      样式文件
                    </div>
                  </div>
                </div>
              </div>
            </GlassCard>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default GlassEffectDemo;
