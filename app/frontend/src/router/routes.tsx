import React from 'react';
import { RouteObject } from 'react-router-dom';
import { Spin } from 'antd';
import type { UserRole } from '../types/index';

// 页面组件
import LoginPage from '../pages/auth/LoginPage';
import MainLayout from '../components/layout/MainLayout';
import ProtectedRoute from '../components/common/ProtectedRoute';
import RouteErrorBoundary from '../components/common/RouteErrorBoundary';

// 关键页面直接导入（避免首次加载时的懒加载延迟）
import DashboardPage from '../pages/dashboard/DashboardPage';
import StudentDashboard from '../pages/students/dashboard/StudentDashboard';
import TeacherDashboard from '../pages/teachers/dashboard/TeacherDashboard';

// 其他页面保持懒加载
const CoursesPage = React.lazy(() => import('../pages/courses/CoursesPage'));
const SchedulesPage = React.lazy(() => import('../pages/schedules/SchedulesPage'));
const AnalyticsPage = React.lazy(() => import('../pages/analytics/AnalyticsPage'));
const ClassroomsPage = React.lazy(() => import('../pages/classrooms/ClassroomsPage'));
const UsersPage = React.lazy(() => import('../pages/users/UsersPage'));
const ProfilePage = React.lazy(() => import('../pages/profile/ProfilePage'));
const NotificationsPage = React.lazy(() => import('../pages/notifications/NotificationsPage'));

// 学生和教师专用页面
const StudentsPage = React.lazy(() => import('../pages/students/StudentsPage'));
const TeachersPage = React.lazy(() => import('../pages/teachers/TeachersPage'));

// 演示和测试页面
const ThemeTestPage = React.lazy(() => import('../pages/demo/ThemeTestPage'));
const UIRedesignShowcase = React.lazy(() => import('../pages/demo/UIRedesignShowcase'));

// 通用的加载组件（优化加载效果）
const LoadingFallback = () => (
  <div
    style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '200px',
      minHeight: '200px',
    }}
  >
    <Spin size="large" />
  </div>
);

// 通用的路由包装器
const RouteWrapper: React.FC<{
  children: React.ReactNode;
  roles?: UserRole[];
}> = ({ children, roles }) => (
  <ProtectedRoute roles={roles}>
    <MainLayout>
      <RouteErrorBoundary>
        <React.Suspense fallback={<LoadingFallback />}>
          {children}
        </React.Suspense>
      </RouteErrorBoundary>
    </MainLayout>
  </ProtectedRoute>
);

// 路由配置接口
interface RouteConfig {
  path: string;
  element: React.ReactElement;
  roles?: UserRole[];
  children?: RouteConfig[];
}

// 路由配置数据
export const routeConfigs: RouteConfig[] = [
  {
    path: '/dashboard',
    element: <DashboardPage />,
    roles: ['admin', 'teacher', 'student'],
  },
  {
    path: '/courses/*',
    element: <CoursesPage />,
    roles: ['admin', 'teacher'],
  },
  {
    path: '/schedules/*',
    element: <SchedulesPage />,
    roles: ['admin', 'teacher', 'student'],
  },
  {
    path: '/analytics',
    element: <AnalyticsPage />,
    roles: ['admin', 'teacher'],
  },
  {
    path: '/classrooms/*',
    element: <ClassroomsPage />,
    roles: ['admin'],
  },
  {
    path: '/users/*',
    element: <UsersPage />,
    roles: ['admin'],
  },
  {
    path: '/profile/*',
    element: <ProfilePage />,
    roles: ['admin', 'teacher', 'student'],
  },
  {
    path: '/notifications/*',
    element: <NotificationsPage />,
    roles: ['admin', 'teacher', 'student'],
  },
  // 学生仪表板
  {
    path: '/students/dashboard',
    element: <StudentDashboard />,
    roles: ['student'],
  },
  // 教师仪表板
  {
    path: '/teachers/dashboard',
    element: <TeacherDashboard />,
    roles: ['teacher'],
  },
  // 学生专用路由
  {
    path: '/students/*',
    element: <StudentsPage />,
    roles: ['student'],
  },
  // 教师专用路由
  {
    path: '/teachers/*',
    element: <TeachersPage />,
    roles: ['teacher'],
  },
  // 演示和测试页面
  {
    path: '/demo/theme-test',
    element: <ThemeTestPage />,
    roles: ['admin', 'teacher', 'student'],
  },
  {
    path: '/demo/ui-redesign-showcase',
    element: <UIRedesignShowcase />,
    roles: ['admin', 'teacher', 'student'],
  },
];

// 生成路由元素的辅助函数
export const createRouteElement = (config: RouteConfig) => (
  <RouteWrapper roles={config.roles}>
    {config.element}
  </RouteWrapper>
);

// 面包屑配置
export const breadcrumbConfig: Record<string, string> = {
  '/dashboard': '仪表板',
  '/courses': '课程管理',
  '/courses/list': '课程列表',
  '/courses/create': '创建课程',
  '/schedules': '课程表管理',
  '/schedules/view': '查看课程表',
  '/schedules/manage': '排课管理',
  '/schedules/conflicts': '冲突检测',
  '/analytics': '数据分析',
  '/classrooms': '教室管理',
  '/classrooms/list': '教室列表',
  '/classrooms/create': '添加教室',
  '/users': '用户管理',
  '/users/list': '用户列表',
  '/users/create': '添加用户',
  '/profile': '个人中心',
  '/profile/info': '个人信息',
  '/profile/password': '修改密码',
  '/profile/settings': '个人设置',
  '/notifications': '通知中心',
  '/notifications/list': '通知列表',
  // 学生页面面包屑
  '/students': '学生中心',
  '/students/dashboard': '学生仪表板',
  '/students/course-selection': '选课系统',
  '/students/my-courses': '我的课程',
  '/students/schedule': '课程表',
  '/students/grades': '成绩查询',
  '/students/profile': '个人信息',
  // 教师页面面包屑
  '/teachers': '教师中心',
  '/teachers/dashboard': '教师仪表板',
  '/teachers/my-courses': '我的课程',
  '/teachers/grade-entry': '成绩录入',
  '/teachers/grade-management': '成绩管理',
  '/teachers/schedule': '教学安排',
  '/teachers/profile': '个人信息',
};

// 菜单权限配置
export const menuPermissions: Record<string, UserRole[]> = {
  '/dashboard': ['admin', 'teacher', 'student'],
  '/courses': ['admin', 'teacher'],
  '/courses/list': ['admin', 'teacher'],
  '/courses/create': ['admin', 'teacher'],
  '/schedules': ['admin', 'teacher', 'student'],
  '/schedules/view': ['admin', 'teacher', 'student'],
  '/schedules/manage': ['admin'],
  '/schedules/conflicts': ['admin'],
  '/analytics': ['admin', 'teacher'],
  '/classrooms': ['admin'],
  '/classrooms/list': ['admin'],
  '/classrooms/create': ['admin'],
  '/users': ['admin'],
  '/users/list': ['admin'],
  '/users/create': ['admin'],
  '/profile': ['admin', 'teacher', 'student'],
  '/profile/info': ['admin', 'teacher', 'student'],
  '/profile/password': ['admin', 'teacher', 'student'],
  '/profile/settings': ['admin', 'teacher', 'student'],
  '/notifications': ['admin', 'teacher', 'student'],
  '/notifications/list': ['admin', 'teacher', 'student'],
  // 学生页面权限
  '/students': ['student'],
  '/students/dashboard': ['student'],
  '/students/course-selection': ['student'],
  '/students/my-courses': ['student'],
  '/students/schedule': ['student'],
  '/students/grades': ['student'],
  '/students/profile': ['student'],
  // 教师页面权限
  '/teachers': ['teacher'],
  '/teachers/dashboard': ['teacher'],
  '/teachers/my-courses': ['teacher'],
  '/teachers/grade-entry': ['teacher'],
  '/teachers/grade-management': ['teacher'],
  '/teachers/schedule': ['teacher'],
  '/teachers/profile': ['teacher'],
  // 演示页面权限
  '/demo/theme-test': ['admin', 'teacher', 'student'],
  '/demo/ui-redesign-showcase': ['admin', 'teacher', 'student'],
};

// 检查用户是否有访问某个路径的权限
export const hasPermission = (path: string, userRole: UserRole): boolean => {
  const permissions = menuPermissions[path];
  return permissions ? permissions.includes(userRole) : false;
};

// 获取用户可访问的菜单项
export const getAccessibleMenuItems = (userRole: UserRole) => {
  return Object.keys(menuPermissions).filter(path => 
    hasPermission(path, userRole)
  );
};
