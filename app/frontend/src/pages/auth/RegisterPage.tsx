import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined, CalendarOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import { DynamicBackground } from '@components/common';
import './RegisterPage.css';

const { Title, Text } = Typography;

interface RegisterForm {
  username: string;
  email: string;
  password: string;
  confirm_password: string;
  first_name?: string;
  last_name?: string;
}

const RegisterPage: React.FC = () => {
  const [form] = Form.useForm<RegisterForm>();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: RegisterForm) => {
    if (values.password !== values.confirm_password) {
      message.error('两次输入的密码不一致');
      return;
    }
    setLoading(true);
    try {
      await authAPI.register({
        username: values.username,
        email: values.email,
        password: values.password,
        first_name: values.first_name || '',
        last_name: values.last_name || '',
      });
      message.success('注册成功，请登录');
      navigate('/login');
    } catch (err: any) {
      message.error(err?.message || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-background">
        <div id="bg-gradient" />
        <DynamicBackground density={0.1} speed={0.9} lineMaxDist={130} triMaxDist={85} opacity={0.55} />
      </div>

      <div className="register-content">
        <Card className="register-card" variant="borderless">
          <div className="register-header">
            <div className="logo-section">
              <CalendarOutlined className="logo-icon" />
              <div className="logo-text">
                <Title level={2} className="system-title">创建账户</Title>
                <Text className="system-subtitle">更轻的玻璃质感 · 灵动简洁</Text>
              </div>
            </div>
          </div>

          <Form
            form={form}
            layout="vertical"
            size="large"
            className="register-form"
            onFinish={onFinish}
          >
            <Form.Item
              name="username"
              label="用户名"
              rules={[{ required: true, message: '请输入用户名' }, { min: 3, message: '至少3个字符' }]}
            >
              <Input prefix={<UserOutlined />} placeholder="请输入用户名" autoComplete="username" />
            </Form.Item>

            <Form.Item
              name="email"
              label="邮箱"
              rules={[{ required: true, message: '请输入邮箱' }, { type: 'email', message: '邮箱格式不正确' }]}
            >
              <Input prefix={<MailOutlined />} placeholder="请输入邮箱" autoComplete="email" />
            </Form.Item>

            <Form.Item
              name="password"
              label="密码"
              rules={[{ required: true, message: '请输入密码' }, { min: 6, message: '至少6个字符' }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" autoComplete="new-password" />
            </Form.Item>

            <Form.Item
              name="confirm_password"
              label="确认密码"
              dependencies={["password"]}
              rules={[{ required: true, message: '请再次输入密码' }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="请再次输入密码" autoComplete="new-password" />
            </Form.Item>

            <div className="form-row">
              <Form.Item name="first_name" label="名" className="half">
                <Input placeholder="可选" />
              </Form.Item>
              <Form.Item name="last_name" label="姓" className="half">
                <Input placeholder="可选" />
              </Form.Item>
            </div>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block className="register-button">
                创建账户
              </Button>
            </Form.Item>

            <div className="register-footer">
              <Text type="secondary">已有账号？</Text>
              <Button type="link" size="small" onClick={() => navigate('/login')}>
                立即登录
              </Button>
            </div>
          </Form>
        </Card>
      </div>
    </div>
  );
};

export default RegisterPage;

