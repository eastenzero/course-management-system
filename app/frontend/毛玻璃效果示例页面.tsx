import React from 'react';
import { Row, Col, Statistic, Progress, Avatar, List, Tag, Button } from 'antd';
import { 
  BookOutlined, 
  TrophyOutlined, 
  ClockCircleOutlined,
  UserOutlined,
  BellOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import { GlassCard } from '@/components/glass/GlassCard';
import { DynamicBackground } from '@/components/common/DynamicBackground';
import './GlassDemo.css';

const GlassDemoPage: React.FC = () => {
  // 模拟数据
  const courseData = [
    { name: '高等数学', progress: 85, color: '#1890ff' },
    { name: '线性代数', progress: 72, color: '#52c41a' },
    { name: '概率论', progress: 68, color: '#faad14' },
    { name: '数据结构', progress: 91, color: '#722ed1' },
  ];

  const recentActivities = [
    { title: '完成了高等数学作业', time: '2小时前', type: 'homework' },
    { title: '参加了线性代数讨论', time: '4小时前', type: 'discussion' },
    { title: '查看了概率论课件', time: '1天前', type: 'study' },
    { title: '提交了数据结构项目', time: '2天前', type: 'project' },
  ];

  return (
    <div className="glass-demo-page">
      {/* 动态背景 */}
      <DynamicBackground 
        density={0.08} 
        speed={0.8} 
        lineMaxDist={120} 
        triMaxDist={80}
        color="rgba(24, 144, 255, 0.6)"
      />
      
      <div className="glass-demo-content">
        {/* 页面标题 */}
        <div className="glass-demo-header">
          <GlassCard variant="primary" className="welcome-banner">
            <div className="welcome-content">
              <Avatar size={64} icon={<UserOutlined />} className="user-avatar" />
              <div className="welcome-text">
                <h1>欢迎回来，张同学！</h1>
                <p>今天是学习的好日子，继续加油吧！</p>
              </div>
              <div className="welcome-stats">
                <div className="stat-item">
                  <span className="stat-number">4</span>
                  <span className="stat-label">今日课程</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">2</span>
                  <span className="stat-label">待办作业</span>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>

        {/* 统计卡片 */}
        <Row gutter={[24, 24]} className="stats-row">
          <Col xs={24} sm={12} lg={6}>
            <GlassCard variant="primary" hoverable>
              <Statistic
                title="本周学习时长"
                value={28.5}
                suffix="小时"
                prefix={<ClockCircleOutlined style={{ color: '#1890ff' }} />}
                valueStyle={{ color: '#1890ff', fontWeight: 'bold' }}
              />
            </GlassCard>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <GlassCard variant="secondary" hoverable>
              <Statistic
                title="完成课程"
                value={12}
                suffix="门"
                prefix={<BookOutlined style={{ color: '#52c41a' }} />}
                valueStyle={{ color: '#52c41a', fontWeight: 'bold' }}
              />
            </GlassCard>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <GlassCard variant="accent" hoverable>
              <Statistic
                title="获得成就"
                value={8}
                suffix="个"
                prefix={<TrophyOutlined style={{ color: '#faad14' }} />}
                valueStyle={{ color: '#faad14', fontWeight: 'bold' }}
              />
            </GlassCard>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <GlassCard variant="primary" hoverable>
              <Statistic
                title="平均分数"
                value={87.2}
                suffix="分"
                precision={1}
                valueStyle={{ color: '#722ed1', fontWeight: 'bold' }}
              />
            </GlassCard>
          </Col>
        </Row>

        {/* 主要内容区域 */}
        <Row gutter={[24, 24]} className="main-content">
          {/* 课程进度 */}
          <Col xs={24} lg={12}>
            <GlassCard 
              title="课程进度" 
              variant="primary"
              extra={<Button type="link">查看全部</Button>}
            >
              <div className="course-progress">
                {courseData.map((course, index) => (
                  <div key={index} className="progress-item">
                    <div className="progress-header">
                      <span className="course-name">{course.name}</span>
                      <span className="progress-value">{course.progress}%</span>
                    </div>
                    <Progress 
                      percent={course.progress} 
                      strokeColor={course.color}
                      showInfo={false}
                      strokeWidth={8}
                    />
                  </div>
                ))}
              </div>
            </GlassCard>
          </Col>

          {/* 最近活动 */}
          <Col xs={24} lg={12}>
            <GlassCard 
              title="最近活动" 
              variant="secondary"
              extra={<BellOutlined style={{ color: '#1890ff' }} />}
            >
              <List
                dataSource={recentActivities}
                renderItem={(item) => (
                  <List.Item className="activity-item">
                    <div className="activity-content">
                      <div className="activity-title">{item.title}</div>
                      <div className="activity-time">
                        <CalendarOutlined /> {item.time}
                      </div>
                    </div>
                    <Tag color={getActivityColor(item.type)}>
                      {getActivityLabel(item.type)}
                    </Tag>
                  </List.Item>
                )}
              />
            </GlassCard>
          </Col>
        </Row>

        {/* 底部卡片 */}
        <Row gutter={[24, 24]} className="bottom-section">
          <Col xs={24}>
            <GlassCard variant="accent" className="announcement-card">
              <div className="announcement-content">
                <h3>📢 系统公告</h3>
                <p>
                  新的学期即将开始，请同学们及时查看课程安排和教学计划。
                  如有任何问题，请联系教务处或相关任课教师。
                </p>
                <div className="announcement-actions">
                  <Button type="primary" ghost>了解详情</Button>
                  <Button type="text">稍后提醒</Button>
                </div>
              </div>
            </GlassCard>
          </Col>
        </Row>
      </div>
    </div>
  );
};

// 辅助函数
const getActivityColor = (type: string) => {
  const colors = {
    homework: 'blue',
    discussion: 'green',
    study: 'orange',
    project: 'purple'
  };
  return colors[type as keyof typeof colors] || 'default';
};

const getActivityLabel = (type: string) => {
  const labels = {
    homework: '作业',
    discussion: '讨论',
    study: '学习',
    project: '项目'
  };
  return labels[type as keyof typeof labels] || '其他';
};

export default GlassDemoPage;
