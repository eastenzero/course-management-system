import React, { useState, useEffect } from 'react';
import { Row, Col, Spin, Alert, Button } from 'antd';
import {
  BookOutlined,
  TrophyOutlined,
  CalendarOutlined,
  UserOutlined,
  StarOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../../store/index';
import { studentAPI } from '../../services/studentAPI';
import { 
  WelcomeHeader, 
  StatisticCard, 
  QuickActions, 
  ModernCard 
} from './index';
import '../../styles/modern.css';

interface StudentDashboardData {
  student_info: {
    user_info: {
      first_name: string;
      student_id: string;
      email: string;
    };
    major: string;
    class_name: string;
    gpa: string;
    total_credits: number;
    completed_credits: number;
    remaining_credits: number;
    completion_rate: number;
  };
  total_courses: number;
  current_semester_courses: number;
  completed_courses: number;
  average_score: string;
  latest_grades: any[];
  today_schedule: any[];
  notifications: any[];
  upcoming_deadlines: any[];
}

const StudentDashboardModern: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<StudentDashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { user } = useAppSelector(state => state.auth);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await studentAPI.getDashboard();
        setDashboardData(response.data);
      } catch (err: any) {
        console.error('获取学生仪表板数据失败:', err);
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
      key: 'course-selection',
      icon: <BookOutlined />,
      title: '选课',
      description: '浏览可选课程，进行在线选课和退课操作',
      onClick: () => navigate('/students/course-selection'),
      variant: 'primary' as const
    },
    {
      key: 'schedule',
      icon: <CalendarOutlined />,
      title: '查看课程表',
      description: '查看个人课程安排，了解上课时间和地点',
      onClick: () => navigate('/students/schedule'),
      variant: 'secondary' as const
    },
    {
      key: 'grades',
      icon: <TrophyOutlined />,
      title: '查看成绩',
      description: '查看各科成绩，了解学习进度和GPA',
      onClick: () => navigate('/students/grades'),
      variant: 'accent' as const
    },
    {
      key: 'my-courses',
      icon: <StarOutlined />,
      title: '我的课程',
      description: '查看已选课程和课程详情',
      onClick: () => navigate('/students/my-courses'),
      variant: 'primary' as const
    },
    {
      key: 'profile',
      icon: <UserOutlined />,
      title: '个人信息',
      description: '查看和编辑您的个人资料',
      onClick: () => navigate('/students/profile'),
      variant: 'secondary' as const
    }
  ];

  return (
    <div className="modern-layout student-layout" style={{ 
      minHeight: '100vh',
      padding: '24px',
      background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    }}>
      {/* 欢迎头部 */}
      <WelcomeHeader
        userType="student"
        userName={dashboardData.student_info.user_info.first_name}
        userInfo={{
          avatar: undefined,
          id: dashboardData.student_info.user_info.student_id,
          email: dashboardData.student_info.user_info.email,
          major: dashboardData.student_info.major,
          className: dashboardData.student_info.class_name
        }}
        todayStats={{
          courses: dashboardData.today_schedule?.length || 0
        }}
      />

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title="总课程数"
            value={dashboardData.total_courses}
            icon={<BookOutlined />}
            variant="courses"
            onClick={() => navigate('/students/my-courses')}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title="本学期课程"
            value={dashboardData.current_semester_courses}
            icon={<CalendarOutlined />}
            variant="students"
            onClick={() => navigate('/students/schedule')}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title="已完成课程"
            value={dashboardData.completed_courses}
            icon={<TrophyOutlined />}
            variant="grades"
            onClick={() => navigate('/students/grades')}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            title="平均成绩"
            value={parseFloat(dashboardData.average_score)}
            icon={<StarOutlined />}
            variant="tasks"
            suffix="分"
            precision={1}
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
            title="学生功能" 
            style={{ height: '100%' }}
            bodyStyle={{ padding: '24px' }}
          >
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
          </ModernCard>
        </Col>
      </Row>
    </div>
  );
};

export default StudentDashboardModern;
