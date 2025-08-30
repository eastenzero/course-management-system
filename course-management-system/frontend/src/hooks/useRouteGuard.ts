import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '../store/index';
import { hasPermission } from '../router/routes';
import type { UserRole } from '../types/index';

/**
 * 路由守卫Hook
 * 用于检查用户权限并处理路由跳转
 */
export const useRouteGuard = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user } = useAppSelector(state => state.auth);

  useEffect(() => {
    // 如果未认证，重定向到登录页
    if (!isAuthenticated) {
      if (location.pathname !== '/login') {
        navigate('/login', { 
          state: { from: location },
          replace: true 
        });
      }
      return;
    }

    // 如果已认证但在登录页，重定向到仪表板
    if (location.pathname === '/login') {
      navigate('/dashboard', { replace: true });
      return;
    }

    // 检查当前路径权限
    if (user && !hasPermission(location.pathname, user.user_type as UserRole)) {
      // 如果没有权限，重定向到仪表板或显示无权限页面
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, user, location.pathname, navigate]);

  return {
    isAuthenticated,
    user,
    hasPermission: (path: string) => 
      user ? hasPermission(path, user.user_type as UserRole) : false,
  };
};

/**
 * 页面权限检查Hook
 * 用于在组件内部检查权限
 */
export const usePagePermission = (requiredRoles: UserRole[]) => {
  const { user } = useAppSelector(state => state.auth);
  
  const hasAccess = user ? requiredRoles.includes(user.user_type as UserRole) : false;
  
  return {
    hasAccess,
    userRole: user?.user_type as UserRole,
    isAdmin: user?.user_type === 'admin',
    isTeacher: user?.user_type === 'teacher',
    isStudent: user?.user_type === 'student',
  };
};

/**
 * 菜单权限Hook
 * 用于过滤菜单项
 */
export const useMenuPermission = () => {
  const { user } = useAppSelector(state => state.auth);
  
  const filterMenuByPermission = (menuItems: any[]) => {
    if (!user) return [];
    
    return menuItems.filter(item => {
      if (item.roles && !item.roles.includes(user.user_type)) {
        return false;
      }
      
      if (item.children) {
        item.children = filterMenuByPermission(item.children);
        return item.children.length > 0;
      }
      
      return true;
    });
  };
  
  return {
    filterMenuByPermission,
    userRole: user?.user_type as UserRole,
  };
};
