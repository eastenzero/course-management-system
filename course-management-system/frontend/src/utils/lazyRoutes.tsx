import React, { Suspense, ComponentType, LazyExoticComponent } from 'react';
import { Spin } from 'antd';
import { ErrorBoundary } from 'react-error-boundary';

// 加载状态组件
const LoadingFallback: React.FC<{ message?: string }> = ({ message = '页面加载中...' }) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      height: '400px',
      gap: '16px',
    }}
  >
    <Spin size="large" />
    <div style={{ color: '#666', fontSize: '14px' }}>{message}</div>
  </div>
);

// 错误状态组件
const ErrorFallback: React.FC<{ error: Error; resetErrorBoundary: () => void }> = ({
  error,
  resetErrorBoundary,
}) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      height: '400px',
      gap: '16px',
      padding: '20px',
    }}
  >
    <div style={{ color: '#ff4d4f', fontSize: '18px', fontWeight: 'bold' }}>
      页面加载失败
    </div>
    <div style={{ color: '#666', fontSize: '14px', textAlign: 'center' }}>
      {error.message}
    </div>
    <button
      onClick={resetErrorBoundary}
      style={{
        padding: '8px 16px',
        backgroundColor: '#1890ff',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
      }}
    >
      重新加载
    </button>
  </div>
);

// 懒加载配置选项
interface LazyLoadOptions {
  /** 加载提示信息 */
  loadingMessage?: string;
  /** 是否启用错误边界 */
  enableErrorBoundary?: boolean;
  /** 预加载延迟时间（毫秒） */
  preloadDelay?: number;
  /** 是否在鼠标悬停时预加载 */
  preloadOnHover?: boolean;
  /** 重试次数 */
  retryCount?: number;
}

// 创建懒加载组件的高阶函数
export function createLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  options: LazyLoadOptions = {}
): LazyExoticComponent<T> {
  const {
    loadingMessage,
    enableErrorBoundary = true,
    preloadDelay = 0,
    preloadOnHover = false,
    retryCount = 3,
  } = options;

  // 创建懒加载组件
  const LazyComponent = React.lazy(() => {
    let retries = 0;
    
    const loadWithRetry = async (): Promise<{ default: T }> => {
      try {
        return await importFn();
      } catch (error) {
        if (retries < retryCount) {
          retries++;
          console.warn(`Component load failed, retrying (${retries}/${retryCount})...`);
          // 延迟重试
          await new Promise(resolve => setTimeout(resolve, 1000 * retries));
          return loadWithRetry();
        }
        throw error;
      }
    };

    return loadWithRetry();
  });

  // 包装组件
  const WrappedComponent: React.FC<any> = (props) => {
    const [shouldPreload, setShouldPreload] = React.useState(false);

    // 预加载逻辑
    React.useEffect(() => {
      if (preloadDelay > 0) {
        const timer = setTimeout(() => {
          setShouldPreload(true);
        }, preloadDelay);
        return () => clearTimeout(timer);
      }
    }, []);

    // 鼠标悬停预加载
    const handleMouseEnter = React.useCallback(() => {
      if (preloadOnHover) {
        setShouldPreload(true);
      }
    }, []);

    const content = (
      <Suspense fallback={<LoadingFallback message={loadingMessage} />}>
        <LazyComponent {...props} />
      </Suspense>
    );

    if (enableErrorBoundary) {
      return (
        <div onMouseEnter={handleMouseEnter}>
          <ErrorBoundary
            FallbackComponent={ErrorFallback}
            onReset={() => window.location.reload()}
          >
            {content}
          </ErrorBoundary>
        </div>
      );
    }

    return <div onMouseEnter={handleMouseEnter}>{content}</div>;
  };

  return WrappedComponent as LazyExoticComponent<T>;
}

// 预定义的懒加载组件
export const LazyDashboard = createLazyComponent(
  () => import('../pages/dashboard/DashboardPage'),
  { loadingMessage: '仪表板加载中...', preloadDelay: 100 }
);

export const LazyCourses = createLazyComponent(
  () => import('../pages/courses/CoursesPage'),
  { loadingMessage: '课程管理加载中...', preloadOnHover: true }
);

export const LazySchedules = createLazyComponent(
  () => import('../pages/schedules/SchedulesPage'),
  { loadingMessage: '课程表管理加载中...', preloadOnHover: true }
);

export const LazyAnalytics = createLazyComponent(
  () => import('../pages/analytics/AnalyticsPage'),
  { loadingMessage: '数据分析加载中...', preloadOnHover: true }
);

export const LazyClassrooms = createLazyComponent(
  () => import('../pages/classrooms/ClassroomsPage'),
  { loadingMessage: '教室管理加载中...', preloadOnHover: true }
);

export const LazyUsers = createLazyComponent(
  () => import('../pages/users/UsersPage'),
  { loadingMessage: '用户管理加载中...', preloadOnHover: true }
);

export const LazyProfile = createLazyComponent(
  () => import('../pages/profile/ProfilePage'),
  { loadingMessage: '个人中心加载中...', preloadOnHover: true }
);

export const LazyNotifications = createLazyComponent(
  () => import('../pages/notifications/NotificationsPage'),
  { loadingMessage: '通知中心加载中...', preloadOnHover: true }
);

// 学生页面
export const LazyStudents = createLazyComponent(
  () => import('../pages/students/StudentsPage'),
  { loadingMessage: '学生中心加载中...', preloadOnHover: true }
);

export const LazyStudentDashboard = createLazyComponent(
  () => import('../pages/students/dashboard/StudentDashboard'),
  { loadingMessage: '学生仪表板加载中...' }
);

// 注释掉不存在的组件，避免构建错误
// export const LazyStudentCourses = createLazyComponent(
//   () => import('../pages/students/courses/StudentCourses'),
//   { loadingMessage: '我的课程加载中...' }
// );

// export const LazyStudentSchedule = createLazyComponent(
//   () => import('../pages/students/schedule/StudentSchedule'),
//   { loadingMessage: '课程表加载中...' }
// );

// export const LazyStudentGrades = createLazyComponent(
//   () => import('../pages/students/grades/StudentGrades'),
//   { loadingMessage: '成绩查询加载中...' }
// );

// 教师页面
export const LazyTeachers = createLazyComponent(
  () => import('../pages/teachers/TeachersPage'),
  { loadingMessage: '教师中心加载中...', preloadOnHover: true }
);

export const LazyTeacherDashboard = createLazyComponent(
  () => import('../pages/teachers/dashboard/TeacherDashboard'),
  { loadingMessage: '教师仪表板加载中...' }
);

export const LazyTeacherCourses = createLazyComponent(
  () => import('../pages/teachers/courses/MyCourses'),
  { loadingMessage: '我的课程加载中...' }
);

export const LazyTeacherSchedule = createLazyComponent(
  () => import('../pages/teachers/courses/CourseSchedule'),
  { loadingMessage: '教学安排加载中...' }
);

export const LazyGradeEntry = createLazyComponent(
  () => import('../pages/teachers/grades/GradeEntry'),
  { loadingMessage: '成绩录入加载中...' }
);

export const LazyGradeManagement = createLazyComponent(
  () => import('../pages/teachers/grades/GradeManagement'),
  { loadingMessage: '成绩管理加载中...' }
);

export const LazyTeacherProfile = createLazyComponent(
  () => import('../pages/teachers/profile/TeacherProfile'),
  { loadingMessage: '个人资料加载中...' }
);

// 路由预加载管理器
export class RoutePreloader {
  private static preloadedRoutes = new Set<string>();
  private static preloadPromises = new Map<string, Promise<any>>();

  // 预加载路由
  static async preloadRoute(routePath: string, importFn: () => Promise<any>): Promise<void> {
    if (this.preloadedRoutes.has(routePath)) {
      return;
    }

    if (this.preloadPromises.has(routePath)) {
      return this.preloadPromises.get(routePath);
    }

    const promise = importFn()
      .then(() => {
        this.preloadedRoutes.add(routePath);
        this.preloadPromises.delete(routePath);
      })
      .catch((error) => {
        console.warn(`Failed to preload route ${routePath}:`, error);
        this.preloadPromises.delete(routePath);
      });

    this.preloadPromises.set(routePath, promise);
    return promise;
  }

  // 批量预加载路由
  static async preloadRoutes(routes: Array<{ path: string; importFn: () => Promise<any> }>): Promise<void> {
    const promises = routes.map(({ path, importFn }) => 
      this.preloadRoute(path, importFn).catch(() => {}) // 忽略单个路由的错误
    );

    await Promise.allSettled(promises);
  }

  // 根据用户角色预加载相关路由
  static async preloadByUserRole(userRole: 'admin' | 'teacher' | 'student'): Promise<void> {
    const commonRoutes = [
      { path: '/dashboard', importFn: () => import('../pages/dashboard/DashboardPage') },
      { path: '/profile', importFn: () => import('../pages/profile/ProfilePage') },
      { path: '/notifications', importFn: () => import('../pages/notifications/NotificationsPage') },
    ];

    const roleSpecificRoutes = {
      admin: [
        { path: '/courses', importFn: () => import('../pages/courses/CoursesPage') },
        { path: '/schedules', importFn: () => import('../pages/schedules/SchedulesPage') },
        { path: '/analytics', importFn: () => import('../pages/analytics/AnalyticsPage') },
        { path: '/classrooms', importFn: () => import('../pages/classrooms/ClassroomsPage') },
        { path: '/users', importFn: () => import('../pages/users/UsersPage') },
      ],
      teacher: [
        { path: '/teachers', importFn: () => import('../pages/teachers/TeachersPage') },
        { path: '/courses', importFn: () => import('../pages/courses/CoursesPage') },
        { path: '/analytics', importFn: () => import('../pages/analytics/AnalyticsPage') },
      ],
      student: [
        { path: '/students', importFn: () => import('../pages/students/StudentsPage') },
      ],
    };

    const roleRoutes = roleSpecificRoutes[userRole] || [];
    const routesToPreload = [...commonRoutes, ...roleRoutes];
    await this.preloadRoutes(routesToPreload);
  }

  // 获取预加载状态
  static getPreloadStatus(): { preloaded: string[]; pending: string[] } {
    return {
      preloaded: Array.from(this.preloadedRoutes),
      pending: Array.from(this.preloadPromises.keys()),
    };
  }
}

// 导出类型
export type { LazyLoadOptions };
