import React, { useState } from 'react';
import { Row, Col, Switch, Typography, Divider } from 'antd';
import {
  BookOutlined,
  UserOutlined,
  CalendarOutlined,
  EditOutlined,
  TeamOutlined,
  TrophyOutlined,
  StarOutlined
} from '@ant-design/icons';
import { 
  WelcomeHeader, 
  StatisticCard, 
  QuickActions, 
  ModernCard,
  ModernButton
} from '../../components/modern';
import '../../styles/modern.css';

const { Title, Paragraph } = Typography;

const ModernUIDemo: React.FC = () => {
  const [userType, setUserType] = useState<'teacher' | 'student'>('teacher');
  const [showAnimations, setShowAnimations] = useState(true);

  const teacherActions = [
    {
      key: 'courses',
      icon: <BookOutlined />,
      title: '我的课程',
      description: '管理您的课程，查看课程信息和学生名单',
      onClick: () => {/* Navigate to courses */},
      variant: 'primary' as const
    },
    {
      key: 'grades',
      icon: <EditOutlined />,
      title: '成绩管理',
      description: '录入和管理学生成绩，生成成绩报告',
      onClick: () => console.log('Navigate to grades'),
      variant: 'secondary' as const
    },
    {
      key: 'schedule',
      icon: <CalendarOutlined />,
      title: '查看课程表',
      description: '查看教学安排，了解上课时间和地点',
      onClick: () => console.log('Navigate to schedule'),
      variant: 'accent' as const
    }
  ];

  const studentActions = [
    {
      key: 'course-selection',
      icon: <BookOutlined />,
      title: '选课',
      description: '浏览可选课程，进行在线选课和退课操作',
      onClick: () => {/* Navigate to course selection */},
      variant: 'primary' as const
    },
    {
      key: 'grades',
      icon: <TrophyOutlined />,
      title: '查看成绩',
      description: '查看各科成绩，了解学习进度和GPA',
      onClick: () => {/* Navigate to grades */},
      variant: 'secondary' as const
    },
    {
      key: 'schedule',
      icon: <CalendarOutlined />,
      title: '查看课程表',
      description: '查看个人课程安排，了解上课时间和地点',
      onClick: () => {/* Navigate to schedule */},
      variant: 'accent' as const
    }
  ];

  const currentActions = userType === 'teacher' ? teacherActions : studentActions;

  return (
    <div className={`modern-layout ${userType}-layout`} style={{ 
      minHeight: '100vh',
      padding: '24px',
      background: userType === 'teacher' 
        ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        : 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    }}>
      {/* 控制面板 */}
      <ModernCard style={{ marginBottom: '24px' }}>
        <Title level={3}>现代化界面演示</Title>
        <Paragraph>
          这是课程管理系统的现代化界面演示。您可以切换用户类型来查看不同的界面风格。
        </Paragraph>
        
        <Row gutter={[16, 16]} align="middle">
          <Col>
            <span>用户类型：</span>
            <Switch
              checkedChildren="学生"
              unCheckedChildren="教师"
              checked={userType === 'student'}
              onChange={(checked) => setUserType(checked ? 'student' : 'teacher')}
            />
          </Col>
          <Col>
            <span>动画效果：</span>
            <Switch
              checked={showAnimations}
              onChange={setShowAnimations}
            />
          </Col>
        </Row>
      </ModernCard>

      {/* 欢迎头部 */}
      <WelcomeHeader
        userType={userType}
        userName={userType === 'teacher' ? '张教授' : '李同学'}
        userInfo={{
          avatar: undefined,
          id: userType === 'teacher' ? 'T001' : 'S001',
          email: userType === 'teacher' ? 'teacher@example.com' : 'student@example.com',
          title: userType === 'teacher' ? '教授' : undefined,
          major: userType === 'student' ? '计算机科学' : undefined,
          className: userType === 'student' ? '计科1班' : undefined
        }}
        todayStats={{
          courses: 3,
          tasks: userType === 'teacher' ? 2 : undefined
        }}
      />

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title={userType === 'teacher' ? '授课总数' : '总课程数'}
            value={userType === 'teacher' ? 8 : 12}
            icon={<BookOutlined />}
            variant="courses"
            onClick={() => {/* Clicked courses card */}}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title="本学期课程"
            value={userType === 'teacher' ? 3 : 5}
            icon={<CalendarOutlined />}
            variant="students"
            onClick={() => {/* Clicked semester card */}}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title={userType === 'teacher' ? '学生总数' : '已完成课程'}
            value={userType === 'teacher' ? 120 : 7}
            icon={userType === 'teacher' ? <TeamOutlined /> : <TrophyOutlined />}
            variant="grades"
            onClick={() => {/* Clicked third card */}}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title={userType === 'teacher' ? '待处理任务' : '平均成绩'}
            value={userType === 'teacher' ? 2 : 87.5}
            icon={userType === 'teacher' ? <EditOutlined /> : <StarOutlined />}
            variant="tasks"
            suffix={userType === 'student' ? '分' : ''}
            precision={userType === 'student' ? 1 : 0}
          />
        </Col>
      </Row>

      {/* 快速操作和功能介绍 */}
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={14}>
          <QuickActions actions={currentActions} title="快速操作" />
        </Col>
        
        <Col xs={24} lg={10}>
          <ModernCard 
            title={`${userType === 'teacher' ? '教师' : '学生'}功能`}
            style={{ height: '100%' }}
            bodyStyle={{ padding: '24px' }}
          >
            {userType === 'teacher' ? (
              <>
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ color: '#262626', marginBottom: '8px' }}>课程管理</h4>
                  <p style={{ color: '#8c8c8c', margin: 0 }}>
                    管理您的课程，查看课程信息和学生名单
                  </p>
                </div>
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ color: '#262626', marginBottom: '8px' }}>成绩管理</h4>
                  <p style={{ color: '#8c8c8c', margin: 0 }}>
                    录入和管理学生成绩，生成成绩报告
                  </p>
                </div>
                <div>
                  <h4 style={{ color: '#262626', marginBottom: '8px' }}>课程表查看</h4>
                  <p style={{ color: '#8c8c8c', margin: 0 }}>
                    查看教学安排，了解上课时间和地点
                  </p>
                </div>
              </>
            ) : (
              <>
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ color: '#262626', marginBottom: '8px' }}>选课系统</h4>
                  <p style={{ color: '#8c8c8c', margin: 0 }}>
                    浏览可选课程，进行在线选课和退课操作
                  </p>
                </div>
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ color: '#262626', marginBottom: '8px' }}>课程表查看</h4>
                  <p style={{ color: '#8c8c8c', margin: 0 }}>
                    查看个人课程安排，了解上课时间和地点
                  </p>
                </div>
                <div>
                  <h4 style={{ color: '#262626', marginBottom: '8px' }}>成绩查询</h4>
                  <p style={{ color: '#8c8c8c', margin: 0 }}>
                    查看各科成绩，了解学习进度和GPA
                  </p>
                </div>
              </>
            )}
          </ModernCard>
        </Col>
      </Row>

      {/* 按钮演示 */}
      <Divider />
      <ModernCard title="按钮样式演示" style={{ marginTop: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col>
            <ModernButton variant="teacher" size="large">
              教师风格按钮
            </ModernButton>
          </Col>
          <Col>
            <ModernButton variant="student" size="large">
              学生风格按钮
            </ModernButton>
          </Col>
          <Col>
            <ModernButton variant="default" size="large">
              默认风格按钮
            </ModernButton>
          </Col>
        </Row>
      </ModernCard>
    </div>
  );
};

export default ModernUIDemo;
