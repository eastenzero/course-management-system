import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAppSelector } from '../../store/index';
import type { UserRole } from '../../types/index';

interface ProtectedRouteProps {
  children: React.ReactNode;
  roles?: UserRole[];
  fallback?: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  roles,
  fallback,
}) => {
  const location = useLocation();
  const { isAuthenticated, user, loading, token } = useAppSelector(
    state => state.auth
  );

  // 如果有token但正在加载用户信息，显示加载状态
  if (token && loading) {
    return fallback || (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        <Spin size="large" tip="正在加载用户信息..." />
      </div>
    );
  }

  // 如果未认证，重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 如果指定了角色要求，检查用户角色
  if (roles && roles.length > 0 && user) {
    if (!roles.includes(user.user_type)) {
      return (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '400px',
            flexDirection: 'column',
            color: '#8c8c8c',
          }}
        >
          <h3>权限不足</h3>
          <p>您没有访问此页面的权限</p>
        </div>
      );
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
