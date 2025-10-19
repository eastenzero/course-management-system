import React, { useState, useEffect } from 'react';
import {
  Row,
  Col,
  Spin,
  Alert,
  Button,
  message,
  Statistic,
  Avatar,
  List,
  Tag,
  Card
} from 'antd';
import {
  BookOutlined,
  TrophyOutlined,
  CalendarOutlined,
  UserOutlined,
  StarOutlined,
  ClockCircleOutlined,
  BellOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../../../store/index';
import { studentAPI } from '../../../services/studentAPI';
import { GlassCard } from '../../../components/glass/GlassCard';
import '../../../styles/glass-theme.css';
import '../../../styles/glass-animations.css';

// 移除不需要的Typography导入

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

const StudentDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<StudentDashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const navigate = useNavigate();
  const { user } = useAppSelector(state => state.auth);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async (isRetry = false) => {
    try {
      setLoading(true);
      setError(null);

      // 设置超时控制
      const timeout = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('请求超时，请检查网络连接')), 8000)
      );

      const dataPromise = studentAPI.getDashboard();
      const response = await Promise.race([dataPromise, timeout]) as any;

      setDashboardData(response.data);
      setRetryCount(0); // 成功后重置重试计数

    } catch (err: any) {
      console.error('获取学生仪表板数据失败:', err);

      const errorMsg = err?.response?.data?.message || err?.message || '获取数据失败';
      setError(errorMsg);

      // 自动重试机制
      if (!isRetry && retryCount < 3) {
        console.log(`学生仪表盘自动重试第${retryCount + 1}次...`);
        setRetryCount(prev => prev + 1);
        setTimeout(() => fetchDashboardData(true), 2000);
        return;
      }

      // 重试失败后使用模拟数据
      if (retryCount >= 3) {
        setMockStudentData();
        message.warning('使用离线数据显示，部分功能可能受限');
      } else {
        message.error('获取仪表板数据失败');
      }
    } finally {
      setLoading(false);
    }
  };

  // 设置模拟学生数据作为降级方案
  const setMockStudentData = () => {
    setDashboardData({
      student_info: {
        user_info: {
          first_name: user?.first_name || '学生',
          student_id: user?.username || 'S000000',
          email: user?.email || 'student@example.com'
        },
        major: '计算机科学与技术',
        class_name: '计科2021-1班',
        gpa: '0.0',
        total_credits: 0,
        completed_credits: 0,
        remaining_credits: 0,
        completion_rate: 0
      },
      total_courses: 0,
      current_semester_courses: 0,
      completed_courses: 0,
      average_score: '0',
      latest_grades: [],
      today_schedule: [],
      notifications: [],
      upcoming_deadlines: []
    });
  };

  // 错误状态显示
  if (error && !loading) {
    return (
      <div style={{
        minHeight: '100vh',
        padding: '50px',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
      }}>
        <Alert
          message="数据加载失败"
          description={`${error}${retryCount > 0 ? ` (已重试${retryCount}次)` : ''}`}
          type="error"
          showIcon
          action={
            <Button
              size="small"
              danger
              onClick={() => {
                setRetryCount(0);
                fetchDashboardData();
              }}
            >
              重试
            </Button>
          }
          style={{ marginBottom: 24 }}
        />
        {/* 显示基础信息，即使API失败 */}
        {dashboardData && (
          <Card title="基础信息（离线模式）">
            <Row gutter={[16, 16]}>
              <Col span={8}>
                <Statistic title="总课程数" value={dashboardData.total_courses} />
              </Col>
              <Col span={8}>
                <Statistic title="本学期课程" value={dashboardData.current_semester_courses} />
              </Col>
              <Col span={8}>
                <Statistic title="已完成课程" value={dashboardData.completed_courses} />
              </Col>
            </Row>
          </Card>
        )}
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
      }}>
        <Card style={{ textAlign: 'center', padding: '20px' }}>
          <Spin size="large" tip={`加载中...${retryCount > 0 ? ` (重试中 ${retryCount}/3)` : ''}`} />
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-page-background">
        <DynamicBackground
          density={0.08}
          speed={0.8}
          lineMaxDist={120}
          triMaxDist={80}
        />
        <div className="glass-content">
          <GlassCard variant="primary" className="glass-animate-slide-in">
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
          </GlassCard>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="glass-page-background">
        <DynamicBackground
          density={0.08}
          speed={0.8}
          lineMaxDist={120}
          triMaxDist={80}
        />
        <div className="glass-content">
          <GlassCard variant="primary">
            <Alert message="暂无数据" type="info" showIcon />
          </GlassCard>
        </div>
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
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      padding: '24px'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* 欢迎横幅 */}
        <Card style={{ marginBottom: '24px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <Avatar size={64} icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
            <div style={{ flex: 1 }}>
              <h1 style={{ margin: 0, fontSize: '28px', fontWeight: 'bold', color: '#1f2937' }}>
                欢迎回来，{dashboardData.student_info.user_info.first_name}！
              </h1>
              <p style={{ margin: '8px 0 0 0', fontSize: '16px', color: '#6b7280' }}>
                {dashboardData.student_info.major} · {dashboardData.student_info.class_name}
              </p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                {dashboardData.today_schedule?.length || 0}
              </div>
              <div style={{ fontSize: '14px', color: '#6b7280' }}>
                今日课程
              </div>
            </div>
          </div>
        </Card>

        {/* 统计卡片 */}
        <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} lg={6}>
            <Card
              hoverable
              style={{ borderRadius: '12px', cursor: 'pointer' }}
              onClick={() => navigate('/students/my-courses')}
            >
              <Statistic
                title="总课程数"
                value={dashboardData.total_courses}
                prefix={<BookOutlined style={{ color: '#1890ff' }} />}
                valueStyle={{ color: '#1890ff', fontWeight: 'bold' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card
              hoverable
              style={{ borderRadius: '12px', cursor: 'pointer' }}
              onClick={() => navigate('/students/schedule')}
            >
              <Statistic
                title="本学期课程"
                value={dashboardData.current_semester_courses}
                prefix={<CalendarOutlined style={{ color: '#52c41a' }} />}
                valueStyle={{ color: '#52c41a', fontWeight: 'bold' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card
              hoverable
              style={{ borderRadius: '12px', cursor: 'pointer' }}
              onClick={() => navigate('/students/grades')}
            >
              <Statistic
                title="已完成课程"
                value={dashboardData.completed_courses}
                prefix={<TrophyOutlined style={{ color: '#faad14' }} />}
                valueStyle={{ color: '#faad14', fontWeight: 'bold' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card hoverable style={{ borderRadius: '12px' }}>
              <Statistic
                title="平均成绩"
                value={parseFloat(dashboardData.average_score)}
                suffix="分"
                precision={1}
                prefix={<StarOutlined style={{ color: '#722ed1' }} />}
                valueStyle={{ color: '#722ed1', fontWeight: 'bold' }}
              />
            </Card>
          </Col>
        </Row>

        {/* 主要内容区域 */}
        <Row gutter={[24, 24]}>
          {/* 快速操作 */}
          <Col xs={24} lg={14}>
            <Card
              title="快速操作"
              style={{ borderRadius: '12px' }}
              extra={<BellOutlined style={{ color: '#1890ff' }} />}
            >
              <Row gutter={[16, 16]}>
                {quickActions.map((action, index) => (
                  <Col xs={24} sm={12} key={action.key}>
                    <div
                      onClick={action.onClick}
                      style={{
                        padding: '16px',
                        background: '#f8fafc',
                        borderRadius: '12px',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        border: '1px solid #e2e8f0'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#e2e8f0';
                        e.currentTarget.style.transform = 'translateY(-2px)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#f8fafc';
                        e.currentTarget.style.transform = 'translateY(0)';
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ color: '#1890ff', fontSize: '20px' }}>
                          {action.icon}
                        </div>
                        <div>
                          <h4 style={{ color: '#1f2937', margin: 0, fontSize: '16px' }}>
                            {action.title}
                          </h4>
                          <p style={{ color: '#6b7280', margin: '4px 0 0 0', fontSize: '12px' }}>
                            {action.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  </Col>
                ))}
              </Row>
            </Card>
          </Col>

          {/* 学习进度 */}
          <Col xs={24} lg={10}>
            <Card
              title="学习进度"
              style={{ borderRadius: '12px' }}
              extra={<ClockCircleOutlined style={{ color: '#1890ff' }} />}
            >
              <div style={{ padding: '16px 0' }}>
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ color: '#1f2937', fontSize: '14px', fontWeight: '500' }}>学分完成度</span>
                    <span style={{ color: '#1890ff', fontSize: '14px', fontWeight: 'bold' }}>
                      {dashboardData.student_info.completion_rate}%
                    </span>
                  </div>
                  <div style={{
                    height: '8px',
                    background: '#e5e7eb',
                    borderRadius: '4px',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      height: '100%',
                      width: `${dashboardData.student_info.completion_rate}%`,
                      background: 'linear-gradient(90deg, #1890ff, #40a9ff)',
                      borderRadius: '4px',
                      transition: 'width 0.3s ease'
                    }} />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ color: '#1890ff', fontSize: '20px', fontWeight: 'bold' }}>
                      {dashboardData.student_info.completed_credits}
                    </div>
                    <div style={{ color: '#6b7280', fontSize: '12px' }}>
                      已完成学分
                    </div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ color: '#52c41a', fontSize: '20px', fontWeight: 'bold' }}>
                      {dashboardData.student_info.remaining_credits}
                    </div>
                    <div style={{ color: '#6b7280', fontSize: '12px' }}>
                      剩余学分
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default StudentDashboard;
