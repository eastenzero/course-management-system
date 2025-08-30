import { api } from './index';
import type { User, LoginForm } from '../types/index';

// 认证相关API
export const authAPI = {
  // 用户登录
  login: (
    credentials: LoginForm
  ): Promise<{ data: { code: number; message: string; data: { access: string; refresh: string; user: User } } }> => {
    return api.post('/auth/login/', credentials);
  },

  // 用户退出
  logout: (): Promise<{ data: any }> => {
    return api.post('/auth/logout/');
  },

  // 刷新token
  refreshToken: (
    refreshToken: string
  ): Promise<{ data: { access: string } }> => {
    return api.post('/auth/refresh/', { refresh: refreshToken });
  },

  // 获取当前用户信息
  getCurrentUser: (): Promise<{ data: { code: number; message: string; data: User } }> => {
    return api.get('/auth/user/');
  },

  // 更新用户信息
  updateProfile: (userData: Partial<User>): Promise<{ data: User }> => {
    return api.patch('/auth/user/', userData);
  },

  // 修改密码
  changePassword: (data: {
    old_password: string;
    new_password: string;
    confirm_password: string;
  }): Promise<{ data: any }> => {
    return api.post('/auth/change-password/', data);
  },

  // 重置密码请求
  requestPasswordReset: (email: string): Promise<{ data: any }> => {
    return api.post('/auth/password-reset/', { email });
  },

  // 确认重置密码
  confirmPasswordReset: (data: {
    token: string;
    new_password: string;
    confirm_password: string;
  }): Promise<{ data: any }> => {
    return api.post('/auth/password-reset-confirm/', data);
  },

  // 用户注册（如果支持）
  register: (userData: {
    username: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role?: string;
  }): Promise<{ data: User }> => {
    return api.post('/auth/register/', userData);
  },

  // 验证邮箱
  verifyEmail: (token: string): Promise<{ data: any }> => {
    return api.post('/auth/verify-email/', { token });
  },

  // 重新发送验证邮件
  resendVerificationEmail: (email: string): Promise<{ data: any }> => {
    return api.post('/auth/resend-verification/', { email });
  },
};
