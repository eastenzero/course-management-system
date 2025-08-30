import { useMemo } from 'react';
import { useAppSelector } from '../store/index';
import type { UserRole } from '../types/index';

export interface Permission {
  /** 权限代码 */
  code: string;
  /** 权限名称 */
  name: string;
  /** 权限描述 */
  description?: string;
  /** 所需角色 */
  roles: UserRole[];
  /** 资源类型 */
  resource?: string;
  /** 操作类型 */
  action?: string;
}

// 系统权限配置
export const PERMISSIONS: Record<string, Permission> = {
  // 课程管理权限
  'course.view': {
    code: 'course.view',
    name: '查看课程',
    roles: ['admin', 'teacher', 'student'],
    resource: 'course',
    action: 'view',
  },
  'course.create': {
    code: 'course.create',
    name: '创建课程',
    roles: ['admin', 'teacher'],
    resource: 'course',
    action: 'create',
  },
  'course.edit': {
    code: 'course.edit',
    name: '编辑课程',
    roles: ['admin', 'teacher'],
    resource: 'course',
    action: 'edit',
  },
  'course.delete': {
    code: 'course.delete',
    name: '删除课程',
    roles: ['admin'],
    resource: 'course',
    action: 'delete',
  },

  // 用户管理权限
  'user.view': {
    code: 'user.view',
    name: '查看用户',
    roles: ['admin'],
    resource: 'user',
    action: 'view',
  },
  'user.create': {
    code: 'user.create',
    name: '创建用户',
    roles: ['admin'],
    resource: 'user',
    action: 'create',
  },
  'user.edit': {
    code: 'user.edit',
    name: '编辑用户',
    roles: ['admin'],
    resource: 'user',
    action: 'edit',
  },
  'user.delete': {
    code: 'user.delete',
    name: '删除用户',
    roles: ['admin'],
    resource: 'user',
    action: 'delete',
  },

  // 教室管理权限
  'classroom.view': {
    code: 'classroom.view',
    name: '查看教室',
    roles: ['admin', 'teacher'],
    resource: 'classroom',
    action: 'view',
  },
  'classroom.create': {
    code: 'classroom.create',
    name: '创建教室',
    roles: ['admin'],
    resource: 'classroom',
    action: 'create',
  },
  'classroom.edit': {
    code: 'classroom.edit',
    name: '编辑教室',
    roles: ['admin'],
    resource: 'classroom',
    action: 'edit',
  },
  'classroom.delete': {
    code: 'classroom.delete',
    name: '删除教室',
    roles: ['admin'],
    resource: 'classroom',
    action: 'delete',
  },

  // 课程表管理权限
  'schedule.view': {
    code: 'schedule.view',
    name: '查看课程表',
    roles: ['admin', 'teacher', 'student'],
    resource: 'schedule',
    action: 'view',
  },
  'schedule.manage': {
    code: 'schedule.manage',
    name: '管理课程表',
    roles: ['admin'],
    resource: 'schedule',
    action: 'manage',
  },
  'schedule.conflict': {
    code: 'schedule.conflict',
    name: '冲突检测',
    roles: ['admin'],
    resource: 'schedule',
    action: 'conflict',
  },

  // 数据分析权限
  'analytics.view': {
    code: 'analytics.view',
    name: '查看数据分析',
    roles: ['admin', 'teacher'],
    resource: 'analytics',
    action: 'view',
  },

  // 系统设置权限
  'system.settings': {
    code: 'system.settings',
    name: '系统设置',
    roles: ['admin'],
    resource: 'system',
    action: 'settings',
  },

  // 成绩管理权限
  'grade.view': {
    code: 'grade.view',
    name: '查看成绩',
    roles: ['admin', 'teacher', 'student'],
    resource: 'grade',
    action: 'view',
  },
  'grade.edit': {
    code: 'grade.edit',
    name: '编辑成绩',
    roles: ['admin', 'teacher'],
    resource: 'grade',
    action: 'edit',
  },
  'grade.manage': {
    code: 'grade.manage',
    name: '管理成绩',
    roles: ['admin', 'teacher'],
    resource: 'grade',
    action: 'manage',
  },

  // 个人资料权限
  'profile.view': {
    code: 'profile.view',
    name: '查看个人资料',
    roles: ['admin', 'teacher', 'student'],
    resource: 'profile',
    action: 'view',
  },
  'profile.edit': {
    code: 'profile.edit',
    name: '编辑个人资料',
    roles: ['admin', 'teacher', 'student'],
    resource: 'profile',
    action: 'edit',
  },
};

/**
 * 权限检查Hook
 * @returns 权限相关的状态和方法
 */
export function usePermission() {
  const { user } = useAppSelector(state => state.auth);
  const userRole = user?.user_type as UserRole;

  // 检查单个权限
  const hasPermission = useMemo(() => {
    return (permissionCode: string): boolean => {
      if (!userRole) return false;
      
      const permission = PERMISSIONS[permissionCode];
      if (!permission) return false;
      
      return permission.roles.includes(userRole);
    };
  }, [userRole]);

  // 检查多个权限（需要全部满足）
  const hasAllPermissions = useMemo(() => {
    return (permissionCodes: string[]): boolean => {
      return permissionCodes.every(code => hasPermission(code));
    };
  }, [hasPermission]);

  // 检查多个权限（满足其中一个即可）
  const hasAnyPermission = useMemo(() => {
    return (permissionCodes: string[]): boolean => {
      return permissionCodes.some(code => hasPermission(code));
    };
  }, [hasPermission]);

  // 检查角色权限
  const hasRole = useMemo(() => {
    return (roles: UserRole | UserRole[]): boolean => {
      if (!userRole) return false;
      
      const roleArray = Array.isArray(roles) ? roles : [roles];
      return roleArray.includes(userRole);
    };
  }, [userRole]);

  // 检查资源权限
  const hasResourcePermission = useMemo(() => {
    return (resource: string, action: string): boolean => {
      if (!userRole) return false;
      
      const permissionCode = `${resource}.${action}`;
      return hasPermission(permissionCode);
    };
  }, [userRole, hasPermission]);

  // 获取用户所有权限
  const userPermissions = useMemo(() => {
    if (!userRole) return [];
    
    return Object.values(PERMISSIONS).filter(permission => 
      permission.roles.includes(userRole)
    );
  }, [userRole]);

  // 获取用户权限代码列表
  const userPermissionCodes = useMemo(() => {
    return userPermissions.map(permission => permission.code);
  }, [userPermissions]);

  // 是否为管理员
  const isAdmin = useMemo(() => {
    return userRole === 'admin';
  }, [userRole]);

  // 是否为教师
  const isTeacher = useMemo(() => {
    return userRole === 'teacher';
  }, [userRole]);

  // 是否为学生
  const isStudent = useMemo(() => {
    return userRole === 'student';
  }, [userRole]);

  return {
    userRole,
    hasPermission,
    hasAllPermissions,
    hasAnyPermission,
    hasRole,
    hasResourcePermission,
    userPermissions,
    userPermissionCodes,
    isAdmin,
    isTeacher,
    isStudent,
  };
}

/**
 * 权限组件包装器Hook
 * @param permissionCode 权限代码
 * @param fallback 无权限时的回退内容
 * @returns 权限检查结果和渲染函数
 */
export function usePermissionWrapper(
  permissionCode: string | string[],
  fallback?: React.ReactNode
) {
  const { hasPermission, hasAnyPermission } = usePermission();
  
  const hasAccess = useMemo(() => {
    if (Array.isArray(permissionCode)) {
      return hasAnyPermission(permissionCode);
    }
    return hasPermission(permissionCode);
  }, [permissionCode, hasPermission, hasAnyPermission]);

  const render = useMemo(() => {
    return (children: React.ReactNode) => {
      return hasAccess ? children : (fallback || null);
    };
  }, [hasAccess, fallback]);

  return {
    hasAccess,
    render,
  };
}

/**
 * 路由权限Hook
 * @param routePath 路由路径
 * @returns 是否有访问权限
 */
export function useRoutePermission(routePath: string): boolean {
  const { userRole } = usePermission();
  
  return useMemo(() => {
    if (!userRole) return false;
    
    // 根据路由路径映射权限
    const routePermissionMap: Record<string, string[]> = {
      '/courses': ['course.view'],
      '/courses/create': ['course.create'],
      '/courses/edit': ['course.edit'],
      '/users': ['user.view'],
      '/users/create': ['user.create'],
      '/classrooms': ['classroom.view'],
      '/classrooms/create': ['classroom.create'],
      '/schedules/manage': ['schedule.manage'],
      '/schedules/conflicts': ['schedule.conflict'],
      '/analytics': ['analytics.view'],
      '/settings': ['system.settings'],
      '/grades': ['grade.view'],
      '/grades/manage': ['grade.manage'],
      '/grades/entry': ['grade.edit'],
      '/profile': ['profile.view'],
      '/profile/edit': ['profile.edit'],
      '/teacher/profile': ['profile.view'],
      '/teacher/courses': ['course.view'],
      '/teacher/schedule': ['schedule.view'],
      '/student/courses': ['course.view'],
      '/student/schedule': ['schedule.view'],
      '/student/grades': ['grade.view'],
    };

    const requiredPermissions = routePermissionMap[routePath];
    if (!requiredPermissions) return true; // 没有配置权限要求的路由默认允许访问

    const { hasAnyPermission } = usePermission();
    return hasAnyPermission(requiredPermissions);
  }, [routePath, userRole]);
}

export default usePermission;
