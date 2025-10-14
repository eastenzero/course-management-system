import React, { useState } from 'react';
import { 
  Row, 
  Col, 
  Typography, 
  Space, 
  Statistic, 
  Progress,
  Table,
  Tag,
  Avatar,
  Timeline,
  Calendar,
  Badge
} from 'antd';
import { 
  BookOutlined,
  TeamOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  CalendarOutlined,
  MessageOutlined,
  FileTextOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import { useTheme } from '../../../hooks/useThemeV2';
import { 
  EnhancedGlassCard,
  EnhancedGlassButton
} from '../../../components/glass';
import DynamicBackground from '../../../components/common/DynamicBackground';
import './ModernTeacherDashboard.css';
import '../../../styles/glass-theme.css';
import '../../../styles/glass-animations.css';

const { Title, Text } = Typography;

const ModernTeacherDashboard: React.FC = () => {
  const { getThemeColors } = useTheme();
  const themeColors = getThemeColors();

  // 模拟数据
  const teacherStats = {
    totalCourses: 8,
    totalStudents: 342,
    pendingGrades: 26,
    completionRate: 78
  };

  const recentCourses = [
    {
      key: '1',
      name: '高等数学A',
      students: 45,
      progress: 85,
      status: '进行中',
      nextClass: '今天 14:00'
    },
    {
      key: '2', 
      name: '线性代数',
      students: 38,
      progress: 92,
      status: '进行中',
      nextClass: '明天 10:00'
    },
    {
      key: '3',
      name: '概率论与数理统计',
      students: 42,
      progress: 76,
      status: '进行中',
      nextClass: '周三 16:00'
    }
  ];

  const recentActivities = [
    {
      type: 'grade',
      content: '批改了《高等数学A》第3章作业',
      time: '2小时前',
      color: themeColors?.primary
    },
    {
      type: 'course',
      content: '发布了《线性代数》新的课件',
      time: '5小时前', 
      color: themeColors?.secondary
    },
    {
      type: 'message',
      content: '回复了学生张三的问题',
      time: '1天前',
      color: themeColors?.accent
    },
    {
      type: 'schedule',
      content: '调整了下周二的课程时间',
      time: '2天前',
      color: themeColors?.tertiary
    }
  ];

  const upcomingClasses = [
    { time: '09:00-10:50', course: '高等数学A', room: 'A101', students: 45 },
    { time: '14:00-15:50', course: '线性代数', room: 'B203', students: 38 },
    { time: '16:00-17:50', course: '概率论', room: 'C305', students: 42 }
  ];

  const courseColumns = [
    {
      title: '课程名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <BookOutlined style={{ color: themeColors?.primary }} />
          <Text strong>{text}</Text>
        </Space>
      )
    },
    {
      title: '学生人数',
      dataIndex: 'students',
      key: 'students',
      render: (count: number) => (
        <Space>
          <TeamOutlined />
          <Text>{count}人</Text>
        </Space>
      )
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
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === '进行中' ? 'processing' : 'success'}>
          {status}
        </Tag>
      )
    },
    {
      title: '下次上课',
      dataIndex: 'nextClass',
      key: 'nextClass',
      render: (time: string) => (
        <Space>
          <ClockCircleOutlined />
          <Text>{time}</Text>
        </Space>
      )
    }
  ];

  return (
    <div className="glass-page-background">
      {/* 动态背景 */}
      <DynamicBackground
        density={0.08}
        speed={0.8}
        lineMaxDist={120}
        triMaxDist={80}
      />
      
      <div className="glass-content modern-teacher-dashboard" style={{ padding: '24px' }}>
      {/* 页面头部 */}
      <div className="dashboard-header">
        <Title level={2} style={{ margin: 0, color: themeColors?.primary }}>
          教师工作台
        </Title>
        <Text type="secondary">欢迎回来，管理您的课程和学生</Text>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} className="stats-section">
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="md" hoverable>
            <Statistic
              title="我的课程"
              value={teacherStats.totalCourses}
              prefix={<BookOutlined style={{ color: themeColors?.primary }} />}
              suffix="门"
              valueStyle={{ color: themeColors?.primary, fontWeight: 'bold' }}
            />
          </EnhancedGlassCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="md" hoverable>
            <Statistic
              title="学生总数"
              value={teacherStats.totalStudents}
              prefix={<TeamOutlined style={{ color: themeColors?.secondary }} />}
              suffix="人"
              valueStyle={{ color: themeColors?.secondary, fontWeight: 'bold' }}
            />
          </EnhancedGlassCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="md" hoverable>
            <Statistic
              title="待批改"
              value={teacherStats.pendingGrades}
              prefix={<FileTextOutlined style={{ color: themeColors?.accent }} />}
              suffix="份"
              valueStyle={{ color: themeColors?.accent, fontWeight: 'bold' }}
            />
          </EnhancedGlassCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="md" hoverable>
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">教学完成率</Text>
              <div style={{ marginTop: 8 }}>
                <Progress
                  type="circle"
                  percent={teacherStats.completionRate}
                  size={80}
                  strokeColor={themeColors?.primary}
                />
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
            <Table
              columns={courseColumns}
              dataSource={recentCourses}
              pagination={false}
              size="middle"
            />
          </EnhancedGlassCard>
        </Col>

        {/* 今日课表 */}
        <Col xs={24} xl={8}>
          <EnhancedGlassCard 
            title={
              <Space>
                <CalendarOutlined />
                <span>今日课表</span>
              </Space>
            }
            glassLevel="md"
          >
            <div className="today-schedule">
              {upcomingClasses.map((class_, index) => (
                <div key={index} className="schedule-item">
                  <div className="schedule-time">
                    <Text strong>{class_.time}</Text>
                  </div>
                  <div className="schedule-details">
                    <Text>{class_.course}</Text>
                    <br />
                    <Text type="secondary">{class_.room} • {class_.students}人</Text>
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
                    activity.type === 'grade' ? <FileTextOutlined /> :
                    activity.type === 'course' ? <BookOutlined /> :
                    activity.type === 'message' ? <MessageOutlined /> :
                    <CalendarOutlined />
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

        {/* 快速操作 */}
        <Col xs={24} xl={12}>
          <EnhancedGlassCard 
            title={
              <Space>
                <TrophyOutlined />
                <span>快速操作</span>
              </Space>
            }
            glassLevel="md"
          >
            <div className="quick-actions">
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <EnhancedGlassButton 
                    type="primary" 
                    block 
                    size="large"
                    icon={<FileTextOutlined />}
                  >
                    批改作业
                  </EnhancedGlassButton>
                </Col>
                <Col span={12}>
                  <EnhancedGlassButton 
                    block 
                    size="large"
                    icon={<BookOutlined />}
                  >
                    发布课件
                  </EnhancedGlassButton>
                </Col>
                <Col span={12}>
                  <EnhancedGlassButton 
                    block 
                    size="large"
                    icon={<CalendarOutlined />}
                  >
                    安排课程
                  </EnhancedGlassButton>
                </Col>
                <Col span={12}>
                  <EnhancedGlassButton 
                    block 
                    size="large"
                    icon={<BarChartOutlined />}
                  >
                    查看统计
                  </EnhancedGlassButton>
                </Col>
              </Row>
            </div>
          </EnhancedGlassCard>
        </Col>
      </Row>
      </div>
    </div>
  );
};

export default ModernTeacherDashboard;