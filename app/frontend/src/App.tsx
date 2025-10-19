import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAppDispatch, useAppSelector } from './store/index';
import { getCurrentUser, initializeAuth } from './store/slices/authSlice';
import { preloadByUserRole, preloadRelatedRoutes } from './utils/routePreloader';
import { printRouteReport } from './utils/routeValidator';
import type { UserRole } from './types/index';

// 页面组件
import LoginPage from './pages/auth/LoginPage';
import TestAccountsPage from './pages/auth/TestAccountsPage';
import RegisterPage from './pages/auth/RegisterPage';
// 演示页面已禁用
// import AuthTest from './pages/demo/AuthTest';
// import ComprehensiveDemo from './pages/demo/ComprehensiveDemo';
// import UIShowcase from './pages/demo/UIShowcase';
// import ModernTeacherDashboard from './pages/teachers/dashboard/ModernTeacherDashboard';
// import ModernStudentDashboard from './pages/students/dashboard/ModernStudentDashboard';

// 路由配置
import { routeConfigs, createRouteElement } from './router/routes';
import { getUserDefaultRoute } from './constants/userRoles';



const App: React.FC = () => {
  const dispatch = useAppDispatch();
  const location = useLocation();
  const { user, loading } = useAppSelector(state => state.auth);

  useEffect(() => {
    // 应用启动时初始化认证状态
    dispatch(initializeAuth());

    // 只有在有token但没有用户信息时，才获取当前用户信息
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    if (token && !userStr) {
      dispatch(getCurrentUser());
    }
  }, [dispatch]);

  // 只在应用首次加载时打印路由报告
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      // 使用setTimeout确保只执行一次
      const timer = setTimeout(() => {
        printRouteReport();
      }, 0);
      
      return () => clearTimeout(timer);
    }
  }, []);

  // 用户登录后预加载相关路由
  useEffect(() => {
    if (user && user.user_type) {
      preloadByUserRole(user.user_type as UserRole);
    }
  }, [user]);

  // 路由变化时预加载相关路由
  useEffect(() => {
    if (user && user.user_type) {
      preloadRelatedRoutes(location.pathname, user.user_type as UserRole);
    }
  }, [location.pathname, user]);

  // 如果正在加载用户信息，显示加载状态
  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          background: '#f5f5f5',
        }}
      >
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return (
    <div className="app">
      <Routes>
        {/* 登录页面 */}
        <Route path="/login" element={<LoginPage />} />

        {/* 注册页面 */}
        <Route path="/register" element={<RegisterPage />} />

        {/* 测试账号页面 - 生产环境下已禁用 */}
        {/* <Route path="/test-accounts" element={<TestAccountsPage />} /> */}

        {/* 演示页面已禁用 */}
        {/* <Route path="/auth-test" element={<AuthTest />} /> */}
        {/* <Route path="/ui-demo" element={<ComprehensiveDemo />} /> */}
        {/* <Route path="/ui-showcase" element={<UIShowcase />} /> */}
        {/* <Route path="/modern-teacher-dashboard" element={<ModernTeacherDashboard />} /> */}
        {/* <Route path="/modern-student-dashboard" element={<ModernStudentDashboard />} /> */}

        {/* 根路径重定向 - 根据用户类型 */}
        <Route
          path="/"
          element={
            user ? (
              <Navigate to={getUserDefaultRoute(user.user_type)} replace />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* 动态生成受保护的路由 */}
        {routeConfigs.map((config) => (
          <Route
            key={config.path}
            path={config.path}
            element={createRouteElement(config)}
          />
        ))}

        {/* 其他未匹配的路由重定向到登录页 */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </div>
  );
};

export default App;
