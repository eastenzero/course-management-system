import React from 'react';
import { Button, Card, Space, Typography, message, Switch } from 'antd';
import { SunOutlined, MoonOutlined } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from '../../store/index';
import { setCredentials, clearCredentials } from '../../store/slices/authSlice';
import { useTheme } from '../../hooks/useThemeV2';

const { Title, Text } = Typography;

const AuthTest: React.FC = () => {
  const dispatch = useAppDispatch();
  const { isAuthenticated, user, token } = useAppSelector(state => state.auth);
  const { uiTheme, toggleMode, getThemeColors } = useTheme();

  const mockLogin = () => {
    // 模拟登录
    const mockUser = {
      id: 1,
      username: 'test_user',
      email: 'test@example.com',
      user_type: 'teacher' as const,
      first_name: '测试',
      last_name: '用户',
      is_active: true,
      date_joined: new Date().toISOString(),
    };
    
    const mockToken = 'mock_jwt_token_' + Date.now();
    
    // 保存到localStorage
    localStorage.setItem('token', mockToken);
    localStorage.setItem('refreshToken', 'mock_refresh_token');
    
    // 更新Redux状态
    dispatch(setCredentials({ user: mockUser, token: mockToken }));
    
    message.success('模拟登录成功！');
  };

  const mockLogout = () => {
    // 清除localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    
    // 清除Redux状态
    dispatch(clearCredentials());
    
    message.success('已退出登录！');
  };

  return (
    <div style={{ padding: '24px', maxWidth: '600px', margin: '0 auto' }}>
      <Title level={2}>认证状态测试</Title>
      
      <Card title="当前认证状态" style={{ marginBottom: '16px' }}>
        <Space direction="vertical" size="small">
          <Text><strong>认证状态：</strong> {isAuthenticated ? '已认证' : '未认证'}</Text>
          <Text><strong>Token：</strong> {token ? `${token.substring(0, 20)}...` : '无'}</Text>
          <Text><strong>用户信息：</strong> {user ? `${user.username} (${user.user_type})` : '无'}</Text>
        </Space>
      </Card>

      <Card title="测试操作">
        <Space>
          <Button type="primary" onClick={mockLogin} disabled={isAuthenticated}>
            模拟登录
          </Button>
          <Button onClick={mockLogout} disabled={!isAuthenticated}>
            退出登录
          </Button>
          <Button onClick={() => window.location.reload()}>
            刷新页面测试
          </Button>
        </Space>
      </Card>

      <Card title="主题测试" style={{ marginTop: '16px' }}>
        <Space direction="vertical" size="middle">
          <div>
            <Text><strong>当前模式：</strong> {uiTheme.mode === 'dark' ? '深色模式' : '浅色模式'}</Text>
          </div>
          <div>
            <Text><strong>当前主题：</strong> {uiTheme.category} - {uiTheme.themeKey}</Text>
          </div>
          <div>
            <Space>
              <Text>切换深浅模式：</Text>
              <Switch
                checked={uiTheme.mode === 'dark'}
                onChange={toggleMode}
                checkedChildren={<MoonOutlined />}
                unCheckedChildren={<SunOutlined />}
              />
            </Space>
          </div>
          <div style={{
            padding: '16px',
            borderRadius: '8px',
            background: `linear-gradient(135deg, ${getThemeColors().primary}20, ${getThemeColors().secondary}20)`,
            border: `1px solid ${getThemeColors().primary}40`
          }}>
            <Text>主题色彩预览区域</Text>
          </div>
        </Space>
      </Card>

      <Card title="使用说明" style={{ marginTop: '16px' }}>
        <Space direction="vertical" size="small">
          <Text><strong>认证测试：</strong></Text>
          <Text>1. 点击"模拟登录"来设置认证状态</Text>
          <Text>2. 点击"刷新页面测试"来验证页面刷新后是否保持登录状态</Text>
          <Text>3. 如果修复成功，刷新后应该不会跳转到登录页</Text>
          <Text><strong>主题测试：</strong></Text>
          <Text>4. 使用开关切换深浅模式，观察整体界面变化</Text>
          <Text>5. 左侧栏应该响应主题切换</Text>
          <Text>6. 所有组件都应该有良好的深色模式支持</Text>
        </Space>
      </Card>
    </div>
  );
};

export default AuthTest;
