import React, { useState, useEffect } from 'react';
import { 
  Row, 
  Col, 
  Typography, 
  Space, 
  Statistic, 
  Progress,
  Tag,
  Avatar,
  Timeline,
  Calendar,
  Badge,
  Tooltip,
  Empty,
  Spin
} from 'antd';
import { 
  BookOutlined,
  TeamOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  CalendarOutlined,
  MessageOutlined,
  FileTextOutlined,
  BarChartOutlined,
  RiseOutlined,
  FallOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { useTheme } from '../../../hooks/useThemeV2';
import { 
  EnhancedGlassCard,
  EnhancedGlassButton,
  EnhancedGlassTable
} from '../../../components/glass';
import './EnhancedTeacherDashboard.css';

const { Title, Text } = Typography;

interface DashboardStats {
  totalCourses: number;
  totalStudents: number;
  pendingGrades: number;
  completionRate: number;
  trend: {
    courses: number;
    students: number;
    grades: number;
    completion: number;
  };
}

interface RecentActivity {
  id: string;
  type: 'grade' | 'course' | 'message' | 'assignment';
  title: string;
  description: string;
  time: string;
  status: 'pending' | 'completed' | 'urgent';
}

const EnhancedTeacherDashboard: React.FC = () => {
  const { getThemeColors, uiTheme } = useTheme();
  const themeColors = getThemeColors();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);

  // 模拟数据加载
  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setStats({
        totalCourses: 8,
        totalStudents: 342,
        pendingGrades: 26,
        completionRate: 78,
        trend: {
          courses: 12.5,
          students: 8.3,
          grades: -15.2,
          completion: 5.7
        }
      });

      setRecentActivities([
        {
          id: '1',
          type: 'grade',
          title: '高等数学期中考试',
          description: '26份试卷待批改',
          time: '2小时前',
          status: 'urgent'
        },
        {
          id: '2',
          type: 'course',
          title: '线性代数课程',
          description: '新增15名学生',
          time: '4小时前',
          status: 'completed'
        },
        {
          id: '3',
          type: 'message',
          title: '学生咨询',
          description: '3条新消息待回复',
          time: '6小时前',
          status: 'pending'
        },
        {
          id: '4',
          type: 'assignment',
          title: '作业布置',
          description: '概率论作业已发布',
          time: '1天前',
          status: 'completed'
        }
      ]);

      setLoading(false);
    };

    loadDashboardData();
  }, []);

  // 获取趋势图标
  const getTrendIcon = (trend: number) => {
    if (trend > 0) {
      return <RiseOutlined style={{ color: '#52c41a' }} />;
    } else if (trend < 0) {
      return <FallOutlined style={{ color: '#ff4d4f' }} />;
    }
    return null;
  };

  // 获取活动图标
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'grade':
        return <FileTextOutlined />;
      case 'course':
        return <BookOutlined />;
      case 'message':
        return <MessageOutlined />;
      case 'assignment':
        return <ClockCircleOutlined />;
      default:
        return <CheckCircleOutlined />;
    }
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'urgent':
        return '#ff4d4f';
      case 'pending':
        return '#faad14';
      case 'completed':
        return '#52c41a';
      default:
        return '#d9d9d9';
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Spin size="large" />
        <Text style={{ marginTop: 16, display: 'block' }}>加载中...</Text>
      </div>
    );
  }

  return (
    <div className="enhanced-teacher-dashboard">
      {/* 欢迎区域 */}
      <div className="dashboard-header">
        <EnhancedGlassCard 
          glassLevel="md" 
          className="welcome-card"
          style={{ 
            background: `linear-gradient(135deg, ${themeColors?.primary}20, ${themeColors?.secondary}20)`
          }}
        >
          <Row align="middle">
            <Col flex="auto">
              <Space direction="vertical" size="small">
                <Title level={2} style={{ margin: 0, color: 'var(--neutral-text-primary)' }}>
                  欢迎回来，张教授
                </Title>
                <Text type="secondary">
                  今天是 {new Date().toLocaleDateString('zh-CN', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric',
                    weekday: 'long'
                  })}
                </Text>
              </Space>
            </Col>
            <Col>
              <Avatar 
                size={64} 
                icon={<TeamOutlined />}
                style={{ backgroundColor: themeColors?.primary }}
              />
            </Col>
          </Row>
        </EnhancedGlassCard>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} className="stats-row">
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="sm" className="stat-card">
            <Statistic
              title="授课课程"
              value={stats?.totalCourses}
              prefix={<BookOutlined style={{ color: themeColors?.primary }} />}
              suffix={
                <Space>
                  {getTrendIcon(stats?.trend.courses || 0)}
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {Math.abs(stats?.trend.courses || 0)}%
                  </Text>
                </Space>
              }
            />
          </EnhancedGlassCard>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="sm" className="stat-card">
            <Statistic
              title="学生总数"
              value={stats?.totalStudents}
              prefix={<TeamOutlined style={{ color: themeColors?.secondary }} />}
              suffix={
                <Space>
                  {getTrendIcon(stats?.trend.students || 0)}
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {Math.abs(stats?.trend.students || 0)}%
                  </Text>
                </Space>
              }
            />
          </EnhancedGlassCard>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="sm" className="stat-card">
            <Statistic
              title="待批改"
              value={stats?.pendingGrades}
              prefix={<FileTextOutlined style={{ color: themeColors?.accent }} />}
              suffix={
                <Space>
                  {getTrendIcon(stats?.trend.grades || 0)}
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {Math.abs(stats?.trend.grades || 0)}%
                  </Text>
                </Space>
              }
            />
          </EnhancedGlassCard>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="sm" className="stat-card">
            <div>
              <Text type="secondary" style={{ fontSize: '14px' }}>完成率</Text>
              <div style={{ marginTop: '8px' }}>
                <Progress 
                  percent={stats?.completionRate} 
                  strokeColor={{
                    '0%': themeColors?.primary,
                    '100%': themeColors?.accent,
                  }}
                  trailColor="rgba(255, 255, 255, 0.1)"
                />
              </div>
              <Space style={{ marginTop: '4px' }}>
                {getTrendIcon(stats?.trend.completion || 0)}
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {Math.abs(stats?.trend.completion || 0)}%
                </Text>
              </Space>
            </div>
          </EnhancedGlassCard>
        </Col>
      </Row>

      {/* 主要内容区域 */}
      <Row gutter={[24, 24]} className="main-content">
        {/* 最近活动 */}
        <Col xs={24} lg={12}>
          <EnhancedGlassCard 
            title="最近活动" 
            glassLevel="md"
            extra={
              <EnhancedGlassButton size="small" type="text">
                查看全部
              </EnhancedGlassButton>
            }
          >
            <Timeline
              items={recentActivities.map(activity => ({
                dot: (
                  <Badge 
                    color={getStatusColor(activity.status)}
                    style={{ 
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '24px',
                      height: '24px'
                    }}
                  >
                    {getActivityIcon(activity.type)}
                  </Badge>
                ),
                children: (
                  <div className="activity-item">
                    <div className="activity-content">
                      <Text strong>{activity.title}</Text>
                      <br />
                      <Text type="secondary">{activity.description}</Text>
                    </div>
                    <Text type="secondary" className="activity-time">
                      {activity.time}
                    </Text>
                  </div>
                )
              }))}
            />
          </EnhancedGlassCard>
        </Col>

        {/* 快速操作 */}
        <Col xs={24} lg={12}>
          <EnhancedGlassCard title="快速操作" glassLevel="md">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <EnhancedGlassButton 
                  block 
                  size="large"
                  icon={<FileTextOutlined />}
                  className="quick-action-btn"
                >
                  批改作业
                </EnhancedGlassButton>
              </Col>
              <Col span={12}>
                <EnhancedGlassButton 
                  block 
                  size="large"
                  icon={<BookOutlined />}
                  className="quick-action-btn"
                >
                  课程管理
                </EnhancedGlassButton>
              </Col>
              <Col span={12}>
                <EnhancedGlassButton 
                  block 
                  size="large"
                  icon={<CalendarOutlined />}
                  className="quick-action-btn"
                >
                  课程表
                </EnhancedGlassButton>
              </Col>
              <Col span={12}>
                <EnhancedGlassButton 
                  block 
                  size="large"
                  icon={<BarChartOutlined />}
                  className="quick-action-btn"
                >
                  数据分析
                </EnhancedGlassButton>
              </Col>
            </Row>
          </EnhancedGlassCard>
        </Col>
      </Row>

      {/* 课程概览 */}
      <Row gutter={[24, 24]} className="course-overview">
        <Col span={24}>
          <EnhancedGlassCard title="课程概览" glassLevel="md">
            <EnhancedGlassTable
              glassLevel="sm"
              hoverEffect
              stickyHeader
              columns={[
                {
                  title: '课程名称',
                  dataIndex: 'name',
                  key: 'name',
                  render: (text: string) => <Text strong>{text}</Text>
                },
                {
                  title: '学生数',
                  dataIndex: 'students',
                  key: 'students',
                  align: 'center'
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
                    <Tag color={status === 'active' ? 'green' : 'orange'}>
                      {status === 'active' ? '进行中' : '待开始'}
                    </Tag>
                  )
                },
                {
                  title: '操作',
                  key: 'action',
                  render: () => (
                    <Space>
                      <EnhancedGlassButton size="small" type="text">
                        查看
                      </EnhancedGlassButton>
                      <EnhancedGlassButton size="small" type="text">
                        编辑
                      </EnhancedGlassButton>
                    </Space>
                  )
                }
              ]}
              dataSource={[
                {
                  key: '1',
                  name: '高等数学A',
                  students: 45,
                  progress: 75,
                  status: 'active'
                },
                {
                  key: '2',
                  name: '线性代数',
                  students: 38,
                  progress: 60,
                  status: 'active'
                },
                {
                  key: '3',
                  name: '概率论与数理统计',
                  students: 42,
                  progress: 30,
                  status: 'active'
                }
              ]}
              pagination={false}
            />
          </EnhancedGlassCard>
        </Col>
      </Row>
    </div>
  );
};

export default EnhancedTeacherDashboard;
