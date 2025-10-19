/**
 * 路由预加载工具
 * 用于提前加载可能访问的页面组件，提升用户体验
 */

import type { UserRole } from '../types/index';

// 预加载配置
interface PreloadConfig {
  component: () => Promise<any>;
  roles?: UserRole[];
  priority: number; // 优先级，数字越小优先级越高
}

// 预加载映射表
const preloadMap: Record<string, PreloadConfig> = {
  dashboard: {
    component: () => import('../pages/dashboard/DashboardPage'),
    roles: ['admin', 'teacher', 'student'],
    priority: 1,
  },
  courses: {
    component: () => import('../pages/courses/CoursesPage'),
    roles: ['admin', 'teacher'],
    priority: 2,
  },
  'courses/list': {
    component: () => import('../pages/courses/CourseListPage'),
    roles: ['admin', 'teacher'],
    priority: 3,
  },
  'courses/create': {
    component: () => import('../pages/courses/CourseCreatePage'),
    roles: ['admin', 'teacher'],
    priority: 4,
  },
  schedules: {
    component: () => import('../pages/schedules/SchedulesPage'),
    roles: ['admin', 'teacher', 'student'],
    priority: 2,
  },
  'schedules/view': {
    component: () => import('../pages/schedules/ScheduleViewPage'),
    roles: ['admin', 'teacher', 'student'],
    priority: 3,
  },
  'schedules/manage': {
    component: () => import('../pages/schedules/ScheduleManagePage'),
    roles: ['admin'],
    priority: 4,
  },
  analytics: {
    component: () => import('../pages/analytics/AnalyticsPage'),
    roles: ['admin', 'teacher'],
    priority: 5,
  },
  classrooms: {
    component: () => import('../pages/classrooms/ClassroomsPage'),
    roles: ['admin'],
    priority: 6,
  },
  users: {
    component: () => import('../pages/users/UsersPage'),
    roles: ['admin'],
    priority: 6,
  },
  profile: {
    component: () => import('../pages/profile/ProfilePage'),
    roles: ['admin', 'teacher', 'student'],
    priority: 7,
  },
};

// 已预加载的组件缓存
const preloadedComponents = new Set<string>();

// 预加载队列
let preloadQueue: string[] = [];
let isPreloading = false;

/**
 * 检查用户是否有权限访问某个路由
 */
const hasPermission = (roles: UserRole[] | undefined, userRole: UserRole): boolean => {
  if (!roles) return true;
  return roles.includes(userRole);
};

/**
 * 预加载单个组件
 */
const preloadComponent = async (routeKey: string): Promise<void> => {
  if (preloadedComponents.has(routeKey)) {
    return;
  }

  const config = preloadMap[routeKey];
  if (!config) {
    return;
  }

  try {
    await config.component();
    preloadedComponents.add(routeKey);
    if (import.meta.env.VITE_VERBOSE_LOGS === 'true') {
      console.log(`✅ Preloaded component: ${routeKey}`);
    }
  } catch (error) {
    if (import.meta.env.VITE_VERBOSE_LOGS === 'true') {
      console.warn(`❌ Failed to preload component: ${routeKey}`, error);
    }
  }
};

/**
 * 处理预加载队列
 */
const processPreloadQueue = async (): Promise<void> => {
  if (isPreloading || preloadQueue.length === 0) {
    return;
  }

  isPreloading = true;

  while (preloadQueue.length > 0) {
    const routeKey = preloadQueue.shift()!;
    await preloadComponent(routeKey);
    
    // 添加小延迟，避免阻塞主线程
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  isPreloading = false;
};

/**
 * 根据用户角色预加载相关组件
 */
export const preloadByUserRole = (userRole: UserRole): void => {
  const routesToPreload = Object.keys(preloadMap)
    .filter(routeKey => {
      const config = preloadMap[routeKey];
      return hasPermission(config.roles, userRole);
    })
    .sort((a, b) => preloadMap[a].priority - preloadMap[b].priority);

  preloadQueue = [...new Set([...preloadQueue, ...routesToPreload])];
  
  // 延迟执行，确保不影响初始页面加载
  setTimeout(() => {
    processPreloadQueue();
  }, 1000);
};

/**
 * 预加载特定路由
 */
export const preloadRoute = (routeKey: string): void => {
  if (!preloadedComponents.has(routeKey) && preloadMap[routeKey]) {
    preloadQueue.push(routeKey);
    processPreloadQueue();
  }
};

/**
 * 预加载相关路由（基于当前路由推测用户可能访问的路由）
 */
export const preloadRelatedRoutes = (currentRoute: string, userRole: UserRole): void => {
  const relatedRoutes: Record<string, string[]> = {
    '/dashboard': ['courses', 'schedules'],
    '/courses': ['courses/list', 'courses/create'],
    '/courses/list': ['courses/create'],
    '/schedules': ['schedules/view', 'schedules/manage'],
    '/schedules/view': ['schedules/manage'],
    '/classrooms': ['classrooms/list', 'classrooms/create'],
    '/users': ['users/list', 'users/create'],
  };

  const related = relatedRoutes[currentRoute] || [];
  related.forEach(routeKey => {
    const config = preloadMap[routeKey];
    if (config && hasPermission(config.roles, userRole)) {
      preloadRoute(routeKey);
    }
  });
};

/**
 * 清理预加载缓存
 */
export const clearPreloadCache = (): void => {
  preloadedComponents.clear();
  preloadQueue = [];
  isPreloading = false;
};

/**
 * 获取预加载状态
 */
export const getPreloadStatus = () => ({
  preloadedCount: preloadedComponents.size,
  queueLength: preloadQueue.length,
  isPreloading,
  preloadedComponents: Array.from(preloadedComponents),
});
