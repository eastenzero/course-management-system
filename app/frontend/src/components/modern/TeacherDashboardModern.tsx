import React, { useState, useEffect } from 'react';
import { Row, Col, Spin, Alert, Button } from 'antd';
import {
  BookOutlined,
  TeamOutlined,
  CalendarOutlined,
  EditOutlined,
  UserOutlined,
  TrophyOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../../store/index';
import { teacherAPI } from '../../services/teacherAPI';
import { 
  WelcomeHeader, 
  StatisticCard, 
  QuickActions, 
  ModernCard 
} from './index';
import '../../styles/modern.css';

interface TeacherDashboardData {
  teacher_info: {
    user_info: {
      first_name: string;
      employee_id: string;
      email: string;
    };
    title_display: string;
    research_area: string;
    office_location: string;
    office_hours: string;
  };
  total_courses: number;
  current_semester_courses: number;
  total_students: number;
  course_statistics: {
    by_type: any;
    by_department: any;
  };
  today_schedule: any[];
  pending_tasks: any[];
  recent_notices: any[];
}

const TeacherDashboardModern: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<TeacherDashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { user } = useAppSelector(state => state.auth);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await teacherAPI.getDashboard();
        setDashboardData(response.data);
      } catch (err: any) {
        console.error('获取教师仪表板数据失败:', err);
        setError(err.message || '获取数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="modern-layout" style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        minHeight: '100vh',
        padding: '50px' 
      }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="modern-layout" style={{ padding: '24px' }}>
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={() => window.location.reload()}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="modern-layout" style={{ padding: '24px' }}>
        <Alert message="暂无数据" type="info" showIcon />
      </div>
    );
  }

  // 快速操作配置
  const quickActions = [
    {
      key: 'courses',
      icon: <BookOutlined />,
      title: '我的课程',
      description: '管理您的课程，查看课程信息和学生名单',
      onClick: () => navigate('/teachers/my-courses'),
      variant: 'primary' as const
    },
    {
      key: 'grades',
      icon: <EditOutlined />,
      title: '成绩管理',
      description: '录入和管理学生成绩，生成成绩报告',
      onClick: () => navigate('/teachers/grade-entry'),
      variant: 'secondary' as const
    },
    {
      key: 'schedule',
      icon: <CalendarOutlined />,
      title: '查看课程表',
      description: '查看教学安排，了解上课时间和地点',
      onClick: () => navigate('/teachers/schedule'),
      variant: 'accent' as const
    },
    {
      key: 'students',
      icon: <TeamOutlined />,
      title: '学生管理',
      description: '查看和管理您的学生信息',
      onClick: () => navigate('/teachers/students'),
      variant: 'primary' as const
    },
    {
      key: 'profile',
      icon: <UserOutlined />,
      title: '个人信息',
      description: '查看和编辑您的个人资料',
      onClick: () => navigate('/teachers/profile'),
      variant: 'secondary' as const
    }
  ];

  return (
    <div className="modern-layout teacher-layout" style={{ 
      minHeight: '100vh',
      padding: '24px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      {/* 欢迎头部 */}
      <WelcomeHeader
        userType="teacher"
        userName={dashboardData.teacher_info.user_info.first_name}
        userInfo={{
          avatar: undefined,
          id: dashboardData.teacher_info.user_info.employee_id,
          email: dashboardData.teacher_info.user_info.email,
          title: dashboardData.teacher_info.title_display
        }}
        todayStats={{
          courses: dashboardData.today_schedule?.length || 0,
          tasks: dashboardData.pending_tasks?.length || 0
        }}
      />

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title="授课总数"
            value={dashboardData.total_courses}
            icon={<BookOutlined />}
            variant="courses"
            onClick={() => navigate('/teachers/my-courses')}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title="本学期课程"
            value={dashboardData.current_semester_courses}
            icon={<CalendarOutlined />}
            variant="students"
            onClick={() => navigate('/teachers/schedule')}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title="学生总数"
            value={dashboardData.total_students}
            icon={<TeamOutlined />}
            variant="grades"
            onClick={() => navigate('/teachers/students')}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title="待处理任务"
            value={dashboardData.pending_tasks?.length || 0}
            icon={<TrophyOutlined />}
            variant="tasks"
          />
        </Col>
      </Row>

      {/* 快速操作和功能介绍 */}
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={14}>
          <QuickActions actions={quickActions} title="快速操作" />
        </Col>
        
        <Col xs={24} lg={10}>
          <ModernCard 
            title="教师功能" 
            style={{ height: '100%' }}
            bodyStyle={{ padding: '24px' }}
          >
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
          </ModernCard>
        </Col>
      </Row>
    </div>
  );
};

export default TeacherDashboardModern;
