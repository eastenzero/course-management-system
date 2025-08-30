import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Alert, Spin, Button, Typography } from 'antd';
import { BookOutlined, UserOutlined, CalendarOutlined, TrophyOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

interface DashboardData {
  totalCourses: number;
  totalStudents: number;
  upcomingClasses: number;
  completedAssignments: number;
}

const TeacherDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);

  useEffect(() => {
    // 模拟数据加载
    setTimeout(() => {
      setDashboardData({
        totalCourses: 5,
        totalStudents: 120,
        upcomingClasses: 8,
        completedAssignments: 45
      });
      setLoading(false);
    }, 1000);
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

  if (!dashboardData) {
    return (
      <div className="modern-layout" style={{ padding: '24px' }}>
        <Alert message="暂无数据" type="info" showIcon />
      </div>
    );
  }

  return (
    <div className="modern-layout" style={{ padding: '24px' }}>
      <Title level={2}>教师工作台</Title>
      
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="我的课程"
              value={dashboardData.totalCourses}
              prefix={<BookOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="学生总数"
              value={dashboardData.totalStudents}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="即将上课"
              value={dashboardData.upcomingClasses}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="已完成作业"
              value={dashboardData.completedAssignments}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <Card title="快速操作" style={{ height: '200px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <Button 
                type="primary" 
                icon={<BookOutlined />}
                onClick={() => navigate('/teachers/my-courses')}
                block
              >
                管理我的课程
              </Button>
              <Button 
                icon={<UserOutlined />}
                onClick={() => navigate('/teachers/students')}
                block
              >
                查看学生信息
              </Button>
              <Button 
                icon={<CalendarOutlined />}
                onClick={() => navigate('/teachers/schedule')}
                block
              >
                查看课程表
              </Button>
            </div>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="最近活动" style={{ height: '200px' }}>
            <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
              暂无最近活动
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default TeacherDashboard;
