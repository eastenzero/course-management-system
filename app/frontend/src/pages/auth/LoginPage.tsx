import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Button,
  Card,
  Checkbox,
  message,
  Typography,
  Space,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../store/index';
import { login } from '../../store/slices/authSlice';
import type { LoginForm } from '../../types/index';
import { getUserDefaultRoute } from '../../constants/userRoles';
import './LoginPage.css';
import { DynamicBackground } from '@components/common';

const { Title, Text } = Typography;

const LoginPage: React.FC = () => {
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  // 生成随机字符串防止浏览器记住表单
  const randomSuffix = React.useMemo(() => Math.random().toString(36).substring(7), []);
  const [loading, setLoading] = useState(false);
  const [loginSuccess, setLoginSuccess] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();

  const { isAuthenticated } = useAppSelector(state => state.auth);

  // 清空表单和禁用浏览器自动填充
  useEffect(() => {
    // 清空表单
    form.resetFields();
    
    // 清空本地存储的记住我状态
    localStorage.removeItem('remember-login');
    
    // 强制清空输入框（防止浏览器缓存）
    setTimeout(() => {
      const usernameInput = document.querySelector('input[placeholder="请输入用户名"]') as HTMLInputElement;
      const passwordInput = document.querySelector('input[placeholder="请输入密码"]') as HTMLInputElement;
      
      if (usernameInput) {
        usernameInput.value = '';
        usernameInput.setAttribute('autocomplete', 'off');
      }
      if (passwordInput) {
        passwordInput.value = '';
        passwordInput.setAttribute('autocomplete', 'new-password');
      }
    }, 100);
  }, [form]);

  useEffect(() => {
    if (loginSuccess) {
      messageApi.success('登录成功');
      setLoginSuccess(false);
    }
  }, [loginSuccess, messageApi]);

  const onFinish = async (values: LoginForm) => {
    setLoading(true);
    try {
      const result = await dispatch(login(values)).unwrap();
      setLoginSuccess(true);

      // 登录成功后立即跳转
      const from = (location.state as any)?.from?.pathname;

      // 如果有指定的来源页面，直接跳转
      if (from) {
        navigate(from, { replace: true });
        return;
      }

      // 根据用户角色跳转到不同的默认页面
      let defaultPath = '/dashboard';
      if (result.user) {
        defaultPath = getUserDefaultRoute(result.user.user_type);
      }

      navigate(defaultPath, { replace: true });
    } catch (error: any) {
      console.error('登录失败:', error);
      
      // 禁用模拟登录，直接显示错误信息
      // message.info('后端服务暂时不可用，自动切换至演示模式');
      // await handleMockLogin(values);
      
      messageApi.error(error?.response?.data?.message || error?.message || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  // 模拟登录功能 - 已禁用
  /*
  const handleMockLogin = async (values: LoginForm) => {
    const { username, password } = values;
    
    // 模拟账号数据库
    const mockAccounts = {
      'teacher1': { password: 'teacher123', user_type: 'teacher', name: '张教授' },
      'admin': { password: 'admin123', user_type: 'admin', name: '管理员' },
      'student1': { password: 'student123', user_type: 'student', name: '李同学' },
    };

    const account = mockAccounts[username as keyof typeof mockAccounts];
    
    if (account && account.password === password) {
      // 创建模拟用户数据
      const mockUser = {
        id: Math.floor(Math.random() * 1000),
        username: username,
        email: `${username}@demo.com`,
        first_name: account.name,
        last_name: '',
        user_type: account.user_type,
        user_type_display: account.user_type === 'teacher' ? '教师' : 
                          account.user_type === 'admin' ? '管理员' : '学生',
        is_active: true,
        date_joined: new Date().toISOString()
      };

      // 模拟token
      const mockToken = `mock_token_${Date.now()}`;
      
      // 存储模拟认证信息
      localStorage.setItem('token', mockToken);
      localStorage.setItem('user', JSON.stringify(mockUser));
      
      // 手动更新Redux状态
      dispatch({ type: 'auth/setCredentials', payload: { user: mockUser, token: mockToken } });
      
      message.success(`欢迎，${account.name}！（演示模式）`);
      
      // 根据用户角色跳转 - 只使用navigate，移除window.location.href
      setTimeout(() => {
        let defaultPath = '/dashboard';
        switch (account.user_type) {
          case 'student':
            defaultPath = '/students/dashboard';
            break;
          case 'teacher':
            defaultPath = '/teachers/dashboard';
            break;
          case 'admin':
            defaultPath = '/dashboard';
            break;
        }
        navigate(defaultPath, { replace: true });
      }, 100); // 减少延时
    } else {
      message.error('用户名或密码错误。请使用演示账号：teacher1/teacher123');
    }
  };
  */

  const onFinishFailed = (errorInfo: any) => {
    console.log('Failed:', errorInfo);
    messageApi.error('请填写完整的登录信息');
  };

  return (
    <div className="login-container">
      {contextHolder}
      {/* 隐藏的假输入框，用来欺骗浏览器自动填充 */}
      <div style={{ position: 'absolute', left: '-9999px', opacity: 0 }}>
        <input type="text" name="fake-username" autoComplete="username" />
        <input type="password" name="fake-password" autoComplete="current-password" />
      </div>
      {/* 动态背景 */}
      <div className="login-background">
        <div id="bg-gradient" />
        <DynamicBackground density={0.12} speed={1} lineMaxDist={140} triMaxDist={90} />
      </div>

      <div className="login-content">
        <Card className="login-card" variant="borderless">
          <div className="login-header">
            <div className="logo-section">
              <CalendarOutlined className="logo-icon" />
              <div className="logo-text">
                <Title level={2} className="system-title">
                  校园课程表管理系统
                </Title>
                <Text className="system-subtitle">
                  Course Management System
                </Text>
              </div>
            </div>
            <Text className="welcome-text">欢迎使用智能化课程表管理平台</Text>
          </div>

          <Form
            form={form}
            name="login-form"
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            layout="vertical"
            size="large"
            className="login-form"
            autoComplete="off"
          >
            <Form.Item
              name="username"
              label="用户名"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="请输入用户名"
                autoComplete="off"
                name={`username-${randomSuffix}`}
                id={`username-${randomSuffix}`}
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="密码"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="请输入密码"
                autoComplete="new-password"
                name={`password-${randomSuffix}`}
                id={`password-${randomSuffix}`}
              />
            </Form.Item>

            <Form.Item>
              <div className="login-options">
                <Form.Item name="remember" valuePropName="checked" noStyle>
                  <Checkbox>记住我（仅记住登录状态）</Checkbox>
                </Form.Item>
                <Button type="link" className="forgot-password">
                  忘记密码？
                </Button>
              </div>
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                className="login-button"
              >
                登录
              </Button>
            </Form.Item>
          </Form>

          <div className="login-footer">
            <div className="login-aux">
              <Text type="secondary">没有账号？</Text>
              <Button type="link" size="small" onClick={() => navigate('/register')}>
                立即注册
              </Button>
            </div>

            <Space split={<span>|</span>} style={{ marginTop: 10 }}>
              <Text type="secondary">请联系管理员获取账号</Text>
            </Space>
            {/* 演示账号信息已禁用
            <div style={{ marginTop: '8px', textAlign: 'center' }}>
              <Button
                type="link"
                size="small"
                onClick={() => navigate('/test-accounts')}
              >
                查看更多测试账号
              </Button>
            </div>
            */}
          </div>
        </Card>

        <div className="login-features">
          <div className="feature-item">
            <div className="feature-icon">📚</div>
            <div className="feature-text">
              <div className="feature-title">智能排课</div>
              <div className="feature-desc">AI算法自动生成最优课程表</div>
            </div>
          </div>

          <div className="feature-item">
            <div className="feature-icon">🔍</div>
            <div className="feature-text">
              <div className="feature-title">冲突检测</div>
              <div className="feature-desc">实时检测并解决排课冲突</div>
            </div>
          </div>

          <div className="feature-item">
            <div className="feature-icon">📊</div>
            <div className="feature-text">
              <div className="feature-title">数据分析</div>
              <div className="feature-desc">全面的教学数据统计分析</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
