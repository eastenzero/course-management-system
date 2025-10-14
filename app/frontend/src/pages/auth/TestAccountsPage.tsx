import React from 'react';
import { Card, Table, Typography, Tag, Button, Space, message } from 'antd';
import { CopyOutlined, LoginOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch } from '../../store/index';
import { login } from '../../store/slices/authSlice';

const { Title, Text } = Typography;

interface TestAccount {
  username: string;
  password: string;
  role: string;
  roleDisplay: string;
  description: string;
  color: string;
}

const TestAccountsPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  const testAccounts: TestAccount[] = [
    {
      username: 'admin',
      password: 'admin123',
      role: 'admin',
      roleDisplay: '超级管理员',
      description: '拥有系统所有权限，可以管理用户、课程、教室等',
      color: 'red'
    },
    {
      username: 'test_teacher',
      password: 'teacher123',
      role: 'teacher',
      roleDisplay: '教师',
      description: '张教授 - 计算机科学与技术学院，可以管理自己的课程',
      color: 'blue'
    },
    {
      username: 'teacher2',
      password: 'teacher123',
      role: 'teacher',
      roleDisplay: '教师',
      description: '李副教授 - 可以管理自己的课程，查看学生信息',
      color: 'blue'
    },
    {
      username: 'teacher3',
      password: 'teacher123',
      role: 'teacher',
      roleDisplay: '教师',
      description: '王讲师 - 可以管理自己的课程，查看学生信息',
      color: 'blue'
    },
    {
      username: 'teacher4',
      password: 'teacher123',
      role: 'teacher',
      roleDisplay: '教师',
      description: '陈教授 - 可以管理自己的课程，查看学生信息',
      color: 'blue'
    },
    {
      username: 'test_student',
      password: 'student123',
      role: 'student',
      roleDisplay: '学生',
      description: '李明同学 - 计算机科学与技术学院，可以选课、查看课程表',
      color: 'green'
    },
    {
      username: 'student2',
      password: 'student123',
      role: 'student',
      roleDisplay: '学生',
      description: '小红 - 可以选课、查看课程表、查看成绩',
      color: 'green'
    },
    {
      username: 'student3',
      password: 'student123',
      role: 'student',
      roleDisplay: '学生',
      description: '小华 - 可以选课、查看课程表、查看成绩',
      color: 'green'
    },
  ];

  const handleCopyCredentials = (username: string, password: string) => {
    const credentials = `用户名: ${username}\n密码: ${password}`;
    navigator.clipboard.writeText(credentials).then(() => {
      message.success('账号信息已复制到剪贴板');
    }).catch(() => {
      message.error('复制失败');
    });
  };

  const handleQuickLogin = async (username: string, password: string) => {
    try {
      await dispatch(login({ username, password })).unwrap();
      message.success(`已登录为 ${username}`);
      // 登录成功后会自动跳转
    } catch (error: any) {
      message.error(error || '登录失败');
    }
  };

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      render: (text: string) => <Text code>{text}</Text>,
    },
    {
      title: '密码',
      dataIndex: 'password',
      key: 'password',
      render: (text: string) => <Text code>{text}</Text>,
    },
    {
      title: '角色',
      dataIndex: 'roleDisplay',
      key: 'role',
      render: (text: string, record: TestAccount) => (
        <Tag color={record.color}>{text}</Tag>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: TestAccount) => (
        <Space>
          <Button
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopyCredentials(record.username, record.password)}
          >
            复制
          </Button>
          <Button
            size="small"
            type="primary"
            icon={<LoginOutlined />}
            onClick={() => handleQuickLogin(record.username, record.password)}
          >
            快速登录
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Card>
        <div style={{ marginBottom: '24px' }}>
          <Title level={2}>测试账号</Title>
          <Text type="secondary">
            以下是系统中可用的测试账号，您可以使用这些账号登录体验不同角色的功能。
          </Text>
        </div>

        <Table
          columns={columns}
          dataSource={testAccounts}
          rowKey="username"
          pagination={false}
          size="middle"
        />

        <div style={{ marginTop: '24px', padding: '16px', backgroundColor: '#f6f8fa', borderRadius: '6px' }}>
          <Title level={4}>使用说明</Title>
          <ul>
            <li><strong>超级管理员</strong>：可以访问所有功能，包括用户管理、课程管理、教室管理等</li>
            <li><strong>教师</strong>：可以管理自己的课程，查看学生信息，进行成绩管理</li>
            <li><strong>学生</strong>：可以进行选课、查看课程表、查看个人成绩等</li>
          </ul>
          <Text type="secondary">
            系统中包含大量测试数据：500+教师、5000+学生、1名管理员，以及1000+课程、教室等数据。
            所有教师账号的密码都是 <Text code>teacher123</Text>，学生账号密码是 <Text code>student123</Text>（管理员密码为 <Text code>admin123</Text>）
          </Text>
        </div>

        <div style={{ marginTop: '16px', textAlign: 'center' }}>
          <Button onClick={() => navigate('/login')}>
            返回登录页面
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default TestAccountsPage;
