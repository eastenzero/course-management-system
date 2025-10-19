import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Button,
  Space,
  Descriptions,
  Tag,
  Tabs,
  Table,
  message,
  Spin,
  Avatar,
  Row,
  Col,
  Statistic,
  Badge,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  UserOutlined,
  BookOutlined,
  CalendarOutlined,
  BarChartOutlined,
  MailOutlined,
  PhoneOutlined,
} from '@ant-design/icons';

const { Title } = Typography;
const { TabPane } = Tabs;

interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  userType: 'admin' | 'teacher' | 'student';
  employeeId?: string;
  studentId?: string;
  isActive: boolean;
  avatar?: string;
  phone?: string;
  department?: string;
  createdAt: string;
  lastLoginAt?: string;
}

interface Course {
  id: string;
  code: string;
  name: string;
  credits: number;
  semester: string;
  role: 'teacher' | 'student';
}

const UserDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 模拟API调用获取用户详情
    const fetchUserDetail = async () => {
      try {
        setLoading(true);
        
        // 模拟数据
        const mockUser: User = {
          id: id || '1',
          username: 'zhang.prof',
          email: 'zhang@school.edu',
          firstName: '教授',
          lastName: '张',
          userType: 'teacher',
          employeeId: 'EMP002',
          isActive: true,
          phone: '13800138002',
          department: '数学系',
          createdAt: '2024-01-15',
          lastLoginAt: '2024-08-14 09:30:00',
        };

        const mockCourses: Course[] = [
          {
            id: '1',
            code: 'MATH101',
            name: '高等数学',
            credits: 4,
            semester: '2024-1',
            role: 'teacher',
          },
          {
            id: '2',
            code: 'MATH201',
            name: '线性代数',
            credits: 3,
            semester: '2024-1',
            role: 'teacher',
          },
          {
            id: '3',
            code: 'MATH301',
            name: '概率论与数理统计',
            credits: 3,
            semester: '2024-2',
            role: 'teacher',
          },
        ];

        setUser(mockUser);
        setCourses(mockCourses);
      } catch (error) {
        message.error('获取用户详情失败');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchUserDetail();
    }
  }, [id]);

  const getUserTypeText = (userType: string): string => {
    const typeMap = {
      admin: '管理员',
      teacher: '教师',
      student: '学生',
    };
    return typeMap[userType as keyof typeof typeMap] || userType;
  };

  const getUserTypeColor = (userType: string): string => {
    const colorMap = {
      admin: 'red',
      teacher: 'blue',
      student: 'green',
    };
    return colorMap[userType as keyof typeof colorMap] || 'default';
  };

  const courseColumns = [
    {
      title: '课程代码',
      dataIndex: 'code',
      key: 'code',
      width: 120,
    },
    {
      title: '课程名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '学分',
      dataIndex: 'credits',
      key: 'credits',
      width: 80,
      align: 'center' as const,
    },
    {
      title: '学期',
      dataIndex: 'semester',
      key: 'semester',
      width: 120,
      render: (semester: string) => (
        <Tag color="blue">{semester}</Tag>
      ),
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 100,
      render: (role: string) => (
        <Tag color={role === 'teacher' ? 'orange' : 'green'}>
          {role === 'teacher' ? '授课教师' : '选课学生'}
        </Tag>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" tip="加载中...">
          <div style={{ minHeight: '200px' }} />
        </Spin>
      </div>
    );
  }

  if (!user) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Title level={3}>用户不存在</Title>
        <Button onClick={() => navigate('/users/list')}>
          返回用户列表
        </Button>
      </div>
    );
  }

  return (
    <div className="user-detail-page">
      <div className="page-header">
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/users/list')}
          >
            返回
          </Button>
          <Title level={2} style={{ margin: 0 }}>
            <Space>
              <Avatar 
                src={user.avatar} 
                icon={<UserOutlined />}
                size="large"
              />
              {user.lastName}{user.firstName}
            </Space>
          </Title>
          <Tag color={getUserTypeColor(user.userType)}>
            {getUserTypeText(user.userType)}
          </Tag>
          <Badge
            status={user.isActive ? 'success' : 'error'}
            text={user.isActive ? '启用' : '禁用'}
          />
        </Space>
        <Space>
          <Button 
            type="primary"
            icon={<EditOutlined />}
            onClick={() => navigate(`/users/${id}/edit`)}
          >
            编辑用户
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="用户类型"
              value={getUserTypeText(user.userType)}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="关联课程"
              value={courses.length}
              suffix="门"
              prefix={<BookOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="账户状态"
              value={user.isActive ? '正常' : '禁用'}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: user.isActive ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="注册时间"
              value={user.createdAt}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Tabs defaultActiveKey="basic">
          <TabPane 
            tab={
              <span>
                <UserOutlined />
                基本信息
              </span>
            } 
            key="basic"
          >
            <Descriptions bordered column={2}>
              <Descriptions.Item label="用户名">{user.username}</Descriptions.Item>
              <Descriptions.Item label="姓名">
                {user.lastName}{user.firstName}
              </Descriptions.Item>
              <Descriptions.Item label="用户类型">
                <Tag color={getUserTypeColor(user.userType)}>
                  {getUserTypeText(user.userType)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="工号/学号">
                {user.employeeId || user.studentId || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="邮箱">
                <Space>
                  <MailOutlined />
                  {user.email}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="手机号">
                <Space>
                  <PhoneOutlined />
                  {user.phone || '-'}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="院系/部门">
                {user.department || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="账户状态">
                <Badge
                  status={user.isActive ? 'success' : 'error'}
                  text={user.isActive ? '启用' : '禁用'}
                />
              </Descriptions.Item>
              <Descriptions.Item label="注册时间">
                {user.createdAt}
              </Descriptions.Item>
              <Descriptions.Item label="最后登录">
                {user.lastLoginAt || '从未登录'}
              </Descriptions.Item>
            </Descriptions>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <BookOutlined />
                关联课程 ({courses.length})
              </span>
            } 
            key="courses"
          >
            <Table
              columns={courseColumns}
              dataSource={courses}
              rowKey="id"
              pagination={{
                total: courses.length,
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 门课程`,
              }}
            />
          </TabPane>

          <TabPane 
            tab={
              <span>
                <BarChartOutlined />
                活动记录
              </span>
            } 
            key="activity"
          >
            <Descriptions bordered column={1}>
              <Descriptions.Item label="最后登录时间">
                {user.lastLoginAt || '从未登录'}
              </Descriptions.Item>
              <Descriptions.Item label="登录次数">
                156 次
              </Descriptions.Item>
              <Descriptions.Item label="账户创建时间">
                {user.createdAt}
              </Descriptions.Item>
              <Descriptions.Item label="密码最后修改">
                2024-08-01
              </Descriptions.Item>
              <Descriptions.Item label="权限变更记录">
                无变更记录
              </Descriptions.Item>
            </Descriptions>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default UserDetailPage;
