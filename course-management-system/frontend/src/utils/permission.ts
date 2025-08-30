import type { UserRole } from '../types/index';

/**
 * 权限工具函数
 */

// 权限常量
export const PERMISSIONS = {
  // 课程管理
  COURSE_VIEW: 'course.view',
  COURSE_CREATE: 'course.create',
  COURSE_EDIT: 'course.edit',
  COURSE_DELETE: 'course.delete',
  
  // 用户管理
  USER_VIEW: 'user.view',
  USER_CREATE: 'user.create',
  USER_EDIT: 'user.edit',
  USER_DELETE: 'user.delete',
  
  // 教室管理
  CLASSROOM_VIEW: 'classroom.view',
  CLASSROOM_CREATE: 'classroom.create',
  CLASSROOM_EDIT: 'classroom.edit',
  CLASSROOM_DELETE: 'classroom.delete',
  
  // 课程表管理
  SCHEDULE_VIEW: 'schedule.view',
  SCHEDULE_MANAGE: 'schedule.manage',
  SCHEDULE_CONFLICT: 'schedule.conflict',
  
  // 数据分析
  ANALYTICS_VIEW: 'analytics.view',
  
  // 系统设置
  SYSTEM_SETTINGS: 'system.settings',

  // 成绩管理
  GRADE_VIEW: 'grade.view',
  GRADE_EDIT: 'grade.edit',
  GRADE_MANAGE: 'grade.manage',

  // 个人资料
  PROFILE_VIEW: 'profile.view',
  PROFILE_EDIT: 'profile.edit',
} as const;

// 角色权限映射
export const ROLE_PERMISSIONS: Record<UserRole, string[]> = {
  admin: [
    PERMISSIONS.COURSE_VIEW,
    PERMISSIONS.COURSE_CREATE,
    PERMISSIONS.COURSE_EDIT,
    PERMISSIONS.COURSE_DELETE,
    PERMISSIONS.USER_VIEW,
    PERMISSIONS.USER_CREATE,
    PERMISSIONS.USER_EDIT,
    PERMISSIONS.USER_DELETE,
    PERMISSIONS.CLASSROOM_VIEW,
    PERMISSIONS.CLASSROOM_CREATE,
    PERMISSIONS.CLASSROOM_EDIT,
    PERMISSIONS.CLASSROOM_DELETE,
    PERMISSIONS.SCHEDULE_VIEW,
    PERMISSIONS.SCHEDULE_MANAGE,
    PERMISSIONS.SCHEDULE_CONFLICT,
    PERMISSIONS.ANALYTICS_VIEW,
    PERMISSIONS.SYSTEM_SETTINGS,
    PERMISSIONS.GRADE_VIEW,
    PERMISSIONS.GRADE_EDIT,
    PERMISSIONS.GRADE_MANAGE,
    PERMISSIONS.PROFILE_VIEW,
    PERMISSIONS.PROFILE_EDIT,
  ],
  teacher: [
    PERMISSIONS.COURSE_VIEW,
    PERMISSIONS.COURSE_CREATE,
    PERMISSIONS.COURSE_EDIT,
    PERMISSIONS.CLASSROOM_VIEW,
    PERMISSIONS.SCHEDULE_VIEW,
    PERMISSIONS.ANALYTICS_VIEW,
    PERMISSIONS.GRADE_VIEW,
    PERMISSIONS.GRADE_EDIT,
    PERMISSIONS.GRADE_MANAGE,
    PERMISSIONS.PROFILE_VIEW,
    PERMISSIONS.PROFILE_EDIT,
  ],
  student: [
    PERMISSIONS.COURSE_VIEW,
    PERMISSIONS.SCHEDULE_VIEW,
    PERMISSIONS.GRADE_VIEW,
    PERMISSIONS.PROFILE_VIEW,
    PERMISSIONS.PROFILE_EDIT,
  ],
};

/**
 * 检查用户是否有指定权限
 * @param userRole 用户角色
 * @param permission 权限代码
 * @returns 是否有权限
 */
export function hasPermission(userRole: UserRole, permission: string): boolean {
  if (!userRole || !permission) return false;
  
  const rolePermissions = ROLE_PERMISSIONS[userRole];
  return rolePermissions ? rolePermissions.includes(permission) : false;
}

/**
 * 检查用户是否有所有指定权限
 * @param userRole 用户角色
 * @param permissions 权限代码数组
 * @returns 是否有所有权限
 */
export function hasAllPermissions(userRole: UserRole, permissions: string[]): boolean {
  return permissions.every(permission => hasPermission(userRole, permission));
}

/**
 * 检查用户是否有任一指定权限
 * @param userRole 用户角色
 * @param permissions 权限代码数组
 * @returns 是否有任一权限
 */
export function hasAnyPermission(userRole: UserRole, permissions: string[]): boolean {
  return permissions.some(permission => hasPermission(userRole, permission));
}

/**
 * 检查用户角色
 * @param userRole 用户角色
 * @param allowedRoles 允许的角色
 * @returns 是否匹配角色
 */
export function hasRole(userRole: UserRole, allowedRoles: UserRole | UserRole[]): boolean {
  if (!userRole) return false;
  
  const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
  return roles.includes(userRole);
}

/**
 * 获取用户所有权限
 * @param userRole 用户角色
 * @returns 权限列表
 */
export function getUserPermissions(userRole: UserRole): string[] {
  return ROLE_PERMISSIONS[userRole] || [];
}

/**
 * 检查是否为管理员
 * @param userRole 用户角色
 * @returns 是否为管理员
 */
export function isAdmin(userRole: UserRole): boolean {
  return userRole === 'admin';
}

/**
 * 检查是否为教师
 * @param userRole 用户角色
 * @returns 是否为教师
 */
export function isTeacher(userRole: UserRole): boolean {
  return userRole === 'teacher';
}

/**
 * 检查是否为学生
 * @param userRole 用户角色
 * @returns 是否为学生
 */
export function isStudent(userRole: UserRole): boolean {
  return userRole === 'student';
}

/**
 * 检查是否为教师或管理员
 * @param userRole 用户角色
 * @returns 是否为教师或管理员
 */
export function isTeacherOrAdmin(userRole: UserRole): boolean {
  return userRole === 'teacher' || userRole === 'admin';
}

/**
 * 过滤有权限的菜单项
 * @param menuItems 菜单项
 * @param userRole 用户角色
 * @returns 过滤后的菜单项
 */
export function filterMenuByPermission<T extends { permission?: string; roles?: UserRole[] }>(
  menuItems: T[],
  userRole: UserRole
): T[] {
  return menuItems.filter(item => {
    // 如果有权限要求，检查权限
    if (item.permission) {
      return hasPermission(userRole, item.permission);
    }
    
    // 如果有角色要求，检查角色
    if (item.roles) {
      return hasRole(userRole, item.roles);
    }
    
    // 没有权限要求的项目默认显示
    return true;
  });
}

/**
 * 检查路由权限
 * @param path 路由路径
 * @param userRole 用户角色
 * @returns 是否有访问权限
 */
export function checkRoutePermission(path: string, userRole: UserRole): boolean {
  // 路由权限映射
  const routePermissions: Record<string, string[]> = {
    '/courses': [PERMISSIONS.COURSE_VIEW],
    '/courses/create': [PERMISSIONS.COURSE_CREATE],
    '/courses/edit': [PERMISSIONS.COURSE_EDIT],
    '/users': [PERMISSIONS.USER_VIEW],
    '/users/create': [PERMISSIONS.USER_CREATE],
    '/users/edit': [PERMISSIONS.USER_EDIT],
    '/classrooms': [PERMISSIONS.CLASSROOM_VIEW],
    '/classrooms/create': [PERMISSIONS.CLASSROOM_CREATE],
    '/classrooms/edit': [PERMISSIONS.CLASSROOM_EDIT],
    '/schedules/manage': [PERMISSIONS.SCHEDULE_MANAGE],
    '/schedules/conflicts': [PERMISSIONS.SCHEDULE_CONFLICT],
    '/analytics': [PERMISSIONS.ANALYTICS_VIEW],
    '/settings': [PERMISSIONS.SYSTEM_SETTINGS],
    '/grades': [PERMISSIONS.GRADE_VIEW],
    '/grades/manage': [PERMISSIONS.GRADE_MANAGE],
    '/grades/entry': [PERMISSIONS.GRADE_EDIT],
    '/profile': [PERMISSIONS.PROFILE_VIEW],
    '/profile/edit': [PERMISSIONS.PROFILE_EDIT],
    '/teacher/profile': [PERMISSIONS.PROFILE_VIEW],
    '/teacher/courses': [PERMISSIONS.COURSE_VIEW],
    '/teacher/schedule': [PERMISSIONS.SCHEDULE_VIEW],
    '/student/courses': [PERMISSIONS.COURSE_VIEW],
    '/student/schedule': [PERMISSIONS.SCHEDULE_VIEW],
    '/student/grades': [PERMISSIONS.GRADE_VIEW],
  };

  const requiredPermissions = routePermissions[path];
  
  // 如果没有配置权限要求，默认允许访问
  if (!requiredPermissions) {
    return true;
  }

  // 检查是否有任一所需权限
  return hasAnyPermission(userRole, requiredPermissions);
}

/**
 * 获取操作权限配置
 * @param userRole 用户角色
 * @returns 操作权限配置
 */
export function getActionPermissions(userRole: UserRole) {
  return {
    // 课程操作权限
    course: {
      canView: hasPermission(userRole, PERMISSIONS.COURSE_VIEW),
      canCreate: hasPermission(userRole, PERMISSIONS.COURSE_CREATE),
      canEdit: hasPermission(userRole, PERMISSIONS.COURSE_EDIT),
      canDelete: hasPermission(userRole, PERMISSIONS.COURSE_DELETE),
    },
    
    // 用户操作权限
    user: {
      canView: hasPermission(userRole, PERMISSIONS.USER_VIEW),
      canCreate: hasPermission(userRole, PERMISSIONS.USER_CREATE),
      canEdit: hasPermission(userRole, PERMISSIONS.USER_EDIT),
      canDelete: hasPermission(userRole, PERMISSIONS.USER_DELETE),
    },
    
    // 教室操作权限
    classroom: {
      canView: hasPermission(userRole, PERMISSIONS.CLASSROOM_VIEW),
      canCreate: hasPermission(userRole, PERMISSIONS.CLASSROOM_CREATE),
      canEdit: hasPermission(userRole, PERMISSIONS.CLASSROOM_EDIT),
      canDelete: hasPermission(userRole, PERMISSIONS.CLASSROOM_DELETE),
    },
    
    // 课程表操作权限
    schedule: {
      canView: hasPermission(userRole, PERMISSIONS.SCHEDULE_VIEW),
      canManage: hasPermission(userRole, PERMISSIONS.SCHEDULE_MANAGE),
      canDetectConflict: hasPermission(userRole, PERMISSIONS.SCHEDULE_CONFLICT),
    },
    
    // 其他权限
    analytics: {
      canView: hasPermission(userRole, PERMISSIONS.ANALYTICS_VIEW),
    },
    
    system: {
      canSettings: hasPermission(userRole, PERMISSIONS.SYSTEM_SETTINGS),
    },
  };
}

/**
 * 权限装饰器工厂
 * @param permission 权限代码
 * @returns 装饰器函数
 */
export function requirePermission(permission: string) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function (this: any, ...args: any[]) {
      // 这里需要获取当前用户角色，实际实现中可能需要从context或store中获取
      const userRole = this.userRole || this.props?.userRole;
      
      if (!hasPermission(userRole, permission)) {
        console.warn(`权限不足: 需要权限 ${permission}`);
        return;
      }
      
      return originalMethod.apply(this, args);
    };
    
    return descriptor;
  };
}

/**
 * 创建权限检查函数
 * @param userRole 用户角色
 * @returns 权限检查函数集合
 */
export function createPermissionChecker(userRole: UserRole) {
  return {
    hasPermission: (permission: string) => hasPermission(userRole, permission),
    hasAllPermissions: (permissions: string[]) => hasAllPermissions(userRole, permissions),
    hasAnyPermission: (permissions: string[]) => hasAnyPermission(userRole, permissions),
    hasRole: (roles: UserRole | UserRole[]) => hasRole(userRole, roles),
    isAdmin: () => isAdmin(userRole),
    isTeacher: () => isTeacher(userRole),
    isStudent: () => isStudent(userRole),
    isTeacherOrAdmin: () => isTeacherOrAdmin(userRole),
    checkRoute: (path: string) => checkRoutePermission(path, userRole),
    getActionPermissions: () => getActionPermissions(userRole),
  };
}
