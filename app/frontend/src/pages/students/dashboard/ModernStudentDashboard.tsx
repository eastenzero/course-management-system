import React, { useState } from 'react';
import { 
  Row, 
  Col, 
  Typography, 
  Space, 
  Statistic, 
  Progress,
  Avatar,
  Timeline,
  Calendar,
  Badge,
  Card,
  Tag
} from 'antd';
import { 
  BookOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  StarOutlined,
  CalendarOutlined,
  MessageOutlined,
  FileTextOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { useTheme } from '../../../hooks/useThemeV2';
import { 
  EnhancedGlassCard,
  EnhancedGlassButton
} from '../../../components/glass';
import './ModernStudentDashboard.css';

const { Title, Text } = Typography;

const ModernStudentDashboard: React.FC = () => {
  const { getThemeColors } = useTheme();
  const themeColors = getThemeColors();

  // 模拟数据
  const studentStats = {
    enrolledCourses: 6,
    completedCourses: 12,
    totalCredits: 24,
    gpa: 3.75
  };

  const currentCourses = [
    {
      id: 1,
      name: '高等数学A',
      teacher: '张教授',
      progress: 75,
      grade: 'A-',
      nextClass: '今天 14:00',
      room: 'A101',
      status: '进行中'
    },
    {
      id: 2,
      name: '大学物理',
      teacher: '李老师', 
      progress: 82,
      grade: 'B+',
      nextClass: '明天 10:00',
      room: 'B203',
      status: '进行中'
    },
    {
      id: 3,
      name: '程序设计基础',
      teacher: '王老师',
      progress: 90,
      grade: 'A',
      nextClass: '周三 16:00',
      room: 'C305',
      status: '进行中'
    }
  ];

  const recentActivities = [
    {
      type: 'assignment',
      content: '提交了《高等数学A》第3章作业',
      time: '2小时前',
      color: themeColors?.primary
    },
    {
      type: 'course',
      content: '完成了《程序设计基础》视频学习',
      time: '5小时前',
      color: themeColors?.secondary
    },
    {
      type: 'grade',
      content: '获得了《大学物理》实验报告A评分',
      time: '1天前',
      color: themeColors?.accent
    },
    {
      type: 'message',
      content: '收到了张教授的课程通知',
      time: '2天前',
      color: themeColors?.tertiary
    }
  ];

  const upcomingEvents = [
    { time: '09:00', event: '高等数学A', type: 'class', room: 'A101' },
    { time: '14:00', event: '大学物理实验', type: 'lab', room: '物理实验室' },
    { time: '16:00', event: '数学作业截止', type: 'deadline', room: '' },
    { time: '19:00', event: '程序设计小组讨论', type: 'study', room: '图书馆' }
  ];

  const achievements = [
    { name: '学习达人', desc: '连续7天完成学习任务', icon: '🏆', color: '#faad14' },
    { name: '全勤王', desc: '本月无缺勤记录', icon: '⭐', color: '#52c41a' },
    { name: '优秀作业', desc: '获得5次作业满分', icon: '📝', color: '#1890ff' },
    { name: '积极参与', desc: '课堂互动次数前10%', icon: '💬', color: '#722ed1' }
  ];

  return (
    <div className="modern-student-dashboard">
      {/* 欢迎区域 */}
      <div className="welcome-section">
        <EnhancedGlassCard glassLevel="lg" className="welcome-card">
          <Row align="middle">
            <Col flex="auto">
              <Space direction="vertical" size="small">
                <Title level={2} style={{ margin: 0, color: themeColors?.primary }}>
                  你好，同学！
                </Title>
                <Text style={{ fontSize: '16px', color: 'var(--neutral-text-secondary)' }}>
                  今天是美好的一天，继续你的学习之旅吧 ✨
                </Text>
                <Space>
                  <Tag color="processing">本学期第12周</Tag>
                  <Tag color="success">GPA: {studentStats.gpa}</Tag>
                </Space>
              </Space>
            </Col>
            <Col>
              <div className="welcome-illustration">
                <div className="study-icon">📚</div>
              </div>
            </Col>
          </Row>
        </EnhancedGlassCard>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} className="stats-section">
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="md" hoverable>
            <Statistic
              title="在读课程"
              value={studentStats.enrolledCourses}
              prefix={<BookOutlined style={{ color: themeColors?.primary }} />}
              suffix="门"
              valueStyle={{ color: themeColors?.primary, fontWeight: 'bold' }}
            />
          </EnhancedGlassCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="md" hoverable>
            <Statistic
              title="已完成课程"
              value={studentStats.completedCourses}
              prefix={<CheckCircleOutlined style={{ color: themeColors?.secondary }} />}
              suffix="门"
              valueStyle={{ color: themeColors?.secondary, fontWeight: 'bold' }}
            />
          </EnhancedGlassCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="md" hoverable>
            <Statistic
              title="获得学分"
              value={studentStats.totalCredits}
              prefix={<TrophyOutlined style={{ color: themeColors?.accent }} />}
              suffix="分"
              valueStyle={{ color: themeColors?.accent, fontWeight: 'bold' }}
            />
          </EnhancedGlassCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="md" hoverable>
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">平均绩点</Text>
              <div style={{ marginTop: 8 }}>
                <div className="gpa-display">
                  <Text style={{ fontSize: '32px', fontWeight: 'bold', color: themeColors?.primary }}>
                    {studentStats.gpa}
                  </Text>
                  <Text type="secondary">/4.0</Text>
                </div>
              </div>
            </div>
          </EnhancedGlassCard>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        {/* 我的课程 */}
        <Col xs={24} xl={16}>
          <EnhancedGlassCard 
            title={
              <Space>
                <BookOutlined />
                <span>我的课程</span>
              </Space>
            }
            extra={
              <EnhancedGlassButton type="text">
                查看全部
              </EnhancedGlassButton>
            }
            glassLevel="lg"
          >
            <div className="course-grid">
              {currentCourses.map((course) => (
                <div key={course.id} className="course-card">
                  <div className="course-header">
                    <div className="course-info">
                      <Text strong className="course-name">{course.name}</Text>
                      <Text type="secondary">{course.teacher}</Text>
                    </div>
                    <div className="course-grade">
                      <Tag color={course.grade.startsWith('A') ? 'success' : 'processing'}>
                        {course.grade}
                      </Tag>
                    </div>
                  </div>
                  <div className="course-progress">
                    <Text type="secondary">学习进度</Text>
                    <Progress 
                      percent={course.progress} 
                      size="small" 
                      strokeColor={themeColors?.primary}
                      showInfo={false}
                    />
                    <Text type="secondary">{course.progress}%</Text>
                  </div>
                  <div className="course-next">
                    <Space>
                      <ClockCircleOutlined />
                      <Text>{course.nextClass}</Text>
                      <Text type="secondary">• {course.room}</Text>
                    </Space>
                  </div>
                </div>
              ))}
            </div>
          </EnhancedGlassCard>
        </Col>

        {/* 今日安排 */}
        <Col xs={24} xl={8}>
          <EnhancedGlassCard 
            title={
              <Space>
                <CalendarOutlined />
                <span>今日安排</span>
              </Space>
            }
            glassLevel="md"
          >
            <div className="daily-schedule">
              {upcomingEvents.map((event, index) => (
                <div key={index} className={`schedule-event ${event.type}`}>
                  <div className="event-time">
                    <Text strong>{event.time}</Text>
                  </div>
                  <div className="event-content">
                    <Text>{event.event}</Text>
                    {event.room && (
                      <Text type="secondary" className="event-room">
                        📍 {event.room}
                      </Text>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </EnhancedGlassCard>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        {/* 最近活动 */}
        <Col xs={24} xl={12}>
          <EnhancedGlassCard 
            title={
              <Space>
                <MessageOutlined />
                <span>最近活动</span>
              </Space>
            }
            glassLevel="md"
          >
            <Timeline>
              {recentActivities.map((activity, index) => (
                <Timeline.Item 
                  key={index} 
                  color={activity.color}
                  dot={
                    activity.type === 'assignment' ? <FileTextOutlined /> :
                    activity.type === 'course' ? <PlayCircleOutlined /> :
                    activity.type === 'grade' ? <TrophyOutlined /> :
                    <MessageOutlined />
                  }
                >
                  <div>
                    <Text>{activity.content}</Text>
                    <br />
                    <Text type="secondary">{activity.time}</Text>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </EnhancedGlassCard>
        </Col>

        {/* 成就徽章 */}
        <Col xs={24} xl={12}>
          <EnhancedGlassCard 
            title={
              <Space>
                <StarOutlined />
                <span>我的成就</span>
              </Space>
            }
            glassLevel="md"
          >
            <div className="achievements-grid">
              {achievements.map((achievement, index) => (
                <div key={index} className="achievement-item">
                  <div 
                    className="achievement-icon"
                    style={{ backgroundColor: achievement.color }}
                  >
                    {achievement.icon}
                  </div>
                  <div className="achievement-info">
                    <Text strong>{achievement.name}</Text>
                    <Text type="secondary">{achievement.desc}</Text>
                  </div>
                </div>
              ))}
            </div>
          </EnhancedGlassCard>
        </Col>
      </Row>

      {/* 快速操作 */}
      <div className="quick-actions-section">
        <EnhancedGlassCard 
          title={
            <Space>
              <PlayCircleOutlined />
              <span>快速操作</span>
            </Space>
          }
          glassLevel="md"
        >
          <Row gutter={[16, 16]}>
            <Col xs={12} sm={6}>
              <EnhancedGlassButton 
                type="primary" 
                block 
                size="large"
                icon={<BookOutlined />}
              >
                继续学习
              </EnhancedGlassButton>
            </Col>
            <Col xs={12} sm={6}>
              <EnhancedGlassButton 
                block 
                size="large"
                icon={<FileTextOutlined />}
              >
                提交作业
              </EnhancedGlassButton>
            </Col>
            <Col xs={12} sm={6}>
              <EnhancedGlassButton 
                block 
                size="large"
                icon={<CalendarOutlined />}
              >
                查看课表
              </EnhancedGlassButton>
            </Col>
            <Col xs={12} sm={6}>
              <EnhancedGlassButton 
                block 
                size="large"
                icon={<TrophyOutlined />}
              >
                查看成绩
              </EnhancedGlassButton>
            </Col>
          </Row>
        </EnhancedGlassCard>
      </div>
    </div>
  );
};

export default ModernStudentDashboard;