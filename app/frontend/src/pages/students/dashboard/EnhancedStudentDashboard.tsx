import React, { useState, useEffect } from 'react';
import { 
  Row, 
  Col, 
  Typography, 
  Space, 
  Progress,
  Tag,
  Avatar,
  Badge,
  Tooltip,
  Empty,
  Spin,
  Rate
} from 'antd';
import { 
  BookOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  CalendarOutlined,
  MessageOutlined,
  FileTextOutlined,
  StarOutlined,
  CheckCircleOutlined,
  PlayCircleOutlined,
  GiftOutlined,
  RocketOutlined,
  HeartOutlined
} from '@ant-design/icons';
import { useTheme } from '../../../hooks/useThemeV2';
import { 
  EnhancedGlassCard,
  EnhancedGlassButton
} from '../../../components/glass';
import './EnhancedStudentDashboard.css';

const { Title, Text } = Typography;

interface StudentStats {
  enrolledCourses: number;
  completedCourses: number;
  totalCredits: number;
  gpa: number;
  achievements: number;
  studyHours: number;
}

interface Course {
  id: string;
  name: string;
  instructor: string;
  progress: number;
  nextClass: string;
  status: 'active' | 'completed' | 'upcoming';
  difficulty: number;
  rating: number;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  date: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

const EnhancedStudentDashboard: React.FC = () => {
  const { getThemeColors, uiTheme } = useTheme();
  const themeColors = getThemeColors();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<StudentStats | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);

  // 模拟数据加载
  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setStats({
        enrolledCourses: 6,
        completedCourses: 12,
        totalCredits: 45,
        gpa: 3.8,
        achievements: 8,
        studyHours: 156
      });

      setCourses([
        {
          id: '1',
          name: '高等数学A',
          instructor: '张教授',
          progress: 75,
          nextClass: '明天 09:00',
          status: 'active',
          difficulty: 4,
          rating: 4.5
        },
        {
          id: '2',
          name: '大学英语',
          instructor: '李老师',
          progress: 60,
          nextClass: '周三 14:00',
          status: 'active',
          difficulty: 3,
          rating: 4.2
        },
        {
          id: '3',
          name: '计算机基础',
          instructor: '王老师',
          progress: 90,
          nextClass: '周五 10:00',
          status: 'active',
          difficulty: 2,
          rating: 4.8
        }
      ]);

      setAchievements([
        {
          id: '1',
          title: '学习达人',
          description: '连续学习7天',
          icon: '🔥',
          date: '2天前',
          rarity: 'rare'
        },
        {
          id: '2',
          title: '完美出勤',
          description: '本月出勤率100%',
          icon: '⭐',
          date: '1周前',
          rarity: 'epic'
        },
        {
          id: '3',
          title: '作业小能手',
          description: '按时提交10次作业',
          icon: '📝',
          date: '2周前',
          rarity: 'common'
        }
      ]);

      setLoading(false);
    };

    loadDashboardData();
  }, []);

  // 获取稀有度颜色
  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'legendary':
        return '#ff6b35';
      case 'epic':
        return '#9c27b0';
      case 'rare':
        return '#2196f3';
      case 'common':
        return '#4caf50';
      default:
        return '#9e9e9e';
    }
  };

  // 获取课程状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#52c41a';
      case 'completed':
        return '#1890ff';
      case 'upcoming':
        return '#faad14';
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
    <div className="enhanced-student-dashboard">
      {/* 欢迎区域 */}
      <div className="dashboard-header">
        <EnhancedGlassCard 
          glassLevel="md" 
          className="welcome-card student-welcome"
          style={{ 
            background: `linear-gradient(135deg, ${themeColors?.primary}15, ${themeColors?.secondary}15)`
          }}
        >
          <Row align="middle">
            <Col flex="auto">
              <Space direction="vertical" size="small">
                <Title level={2} style={{ margin: 0, color: 'var(--neutral-text-primary)' }}>
                  你好，小明同学！ 🎓
                </Title>
                <Text type="secondary">
                  今天也要加油学习哦～ 距离期末考试还有 <Text strong>23天</Text>
                </Text>
                <Space>
                  <Badge count={stats?.achievements} color={themeColors?.accent}>
                    <Text>成就徽章</Text>
                  </Badge>
                  <Text type="secondary">|</Text>
                  <Text>学习时长: <Text strong>{stats?.studyHours}小时</Text></Text>
                </Space>
              </Space>
            </Col>
            <Col>
              <div className="student-avatar-wrapper">
                <Avatar 
                  size={64} 
                  icon={<RocketOutlined />}
                  style={{ backgroundColor: themeColors?.primary }}
                />
                <div className="level-badge">
                  <Text strong style={{ color: 'white', fontSize: '12px' }}>Lv.{Math.floor((stats?.studyHours || 0) / 20)}</Text>
                </div>
              </div>
            </Col>
          </Row>
        </EnhancedGlassCard>
      </div>

      {/* 学习统计 */}
      <Row gutter={[24, 24]} className="stats-row">
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="sm" className="stat-card student-stat">
            <div className="stat-content">
              <div className="stat-icon" style={{ backgroundColor: themeColors?.primary }}>
                <BookOutlined />
              </div>
              <div className="stat-info">
                <Text type="secondary">在读课程</Text>
                <Title level={3} style={{ margin: 0 }}>{stats?.enrolledCourses}</Title>
              </div>
            </div>
          </EnhancedGlassCard>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="sm" className="stat-card student-stat">
            <div className="stat-content">
              <div className="stat-icon" style={{ backgroundColor: themeColors?.secondary }}>
                <TrophyOutlined />
              </div>
              <div className="stat-info">
                <Text type="secondary">GPA</Text>
                <Title level={3} style={{ margin: 0 }}>{stats?.gpa}</Title>
              </div>
            </div>
          </EnhancedGlassCard>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="sm" className="stat-card student-stat">
            <div className="stat-content">
              <div className="stat-icon" style={{ backgroundColor: themeColors?.accent }}>
                <StarOutlined />
              </div>
              <div className="stat-info">
                <Text type="secondary">获得学分</Text>
                <Title level={3} style={{ margin: 0 }}>{stats?.totalCredits}</Title>
              </div>
            </div>
          </EnhancedGlassCard>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <EnhancedGlassCard glassLevel="sm" className="stat-card student-stat">
            <div className="stat-content">
              <div className="stat-icon" style={{ backgroundColor: themeColors?.tertiary }}>
                <GiftOutlined />
              </div>
              <div className="stat-info">
                <Text type="secondary">成就数量</Text>
                <Title level={3} style={{ margin: 0 }}>{stats?.achievements}</Title>
              </div>
            </div>
          </EnhancedGlassCard>
        </Col>
      </Row>

      {/* 主要内容区域 */}
      <Row gutter={[24, 24]} className="main-content">
        {/* 我的课程 */}
        <Col xs={24} lg={16}>
          <EnhancedGlassCard 
            title="我的课程" 
            glassLevel="md"
            extra={
              <EnhancedGlassButton size="small" type="text">
                查看全部
              </EnhancedGlassButton>
            }
          >
            <div className="course-list">
              {courses.map(course => (
                <div key={course.id} className="course-item">
                  <div className="course-header">
                    <div className="course-info">
                      <Title level={5} style={{ margin: 0 }}>{course.name}</Title>
                      <Text type="secondary">{course.instructor}</Text>
                    </div>
                    <div className="course-meta">
                      <Rate disabled defaultValue={course.rating} style={{ fontSize: '12px' }} />
                      <Tag color={getStatusColor(course.status)}>
                        {course.status === 'active' ? '进行中' : 
                         course.status === 'completed' ? '已完成' : '即将开始'}
                      </Tag>
                    </div>
                  </div>
                  
                  <div className="course-progress">
                    <div className="progress-info">
                      <Text type="secondary">学习进度</Text>
                      <Text strong>{course.progress}%</Text>
                    </div>
                    <Progress 
                      percent={course.progress} 
                      strokeColor={{
                        '0%': themeColors?.primary,
                        '100%': themeColors?.secondary,
                      }}
                      trailColor="rgba(255, 255, 255, 0.1)"
                      size="small"
                    />
                  </div>
                  
                  <div className="course-footer">
                    <Space>
                      <ClockCircleOutlined />
                      <Text type="secondary">下次课程: {course.nextClass}</Text>
                    </Space>
                    <EnhancedGlassButton 
                      size="small" 
                      icon={<PlayCircleOutlined />}
                      type="primary"
                    >
                      继续学习
                    </EnhancedGlassButton>
                  </div>
                </div>
              ))}
            </div>
          </EnhancedGlassCard>
        </Col>

        {/* 成就与奖励 */}
        <Col xs={24} lg={8}>
          <EnhancedGlassCard 
            title="最新成就" 
            glassLevel="md"
            extra={
              <EnhancedGlassButton size="small" type="text">
                查看全部
              </EnhancedGlassButton>
            }
          >
            <div className="achievement-list">
              {achievements.map(achievement => (
                <div key={achievement.id} className="achievement-item">
                  <div className="achievement-icon" style={{ backgroundColor: getRarityColor(achievement.rarity) }}>
                    <span style={{ fontSize: '20px' }}>{achievement.icon}</span>
                  </div>
                  <div className="achievement-content">
                    <Text strong>{achievement.title}</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {achievement.description}
                    </Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '11px' }}>
                      {achievement.date}
                    </Text>
                  </div>
                </div>
              ))}
            </div>
          </EnhancedGlassCard>
        </Col>
      </Row>
    </div>
  );
};

export default EnhancedStudentDashboard;
