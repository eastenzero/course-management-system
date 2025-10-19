// 用户角色常量定义
export const USER_ROLES = {
  ADMIN: 'admin',
  ACADEMIC_ADMIN: 'academic_admin', 
  TEACHER: 'teacher',
  STUDENT: 'student'
} as const;

// 角色类型
export type UserRole = typeof USER_ROLES[keyof typeof USER_ROLES];

// 角色对应的默认路由
export const ROLE_ROUTES = {
  [USER_ROLES.ADMIN]: '/dashboard',
  [USER_ROLES.ACADEMIC_ADMIN]: '/dashboard',
  [USER_ROLES.TEACHER]: '/teachers/dashboard',
  [USER_ROLES.STUDENT]: '/students/dashboard'
} as const;

// 判断是否为管理员角色
export const isAdminRole = (userType: string): boolean => {
  return userType === USER_ROLES.ADMIN || userType === USER_ROLES.ACADEMIC_ADMIN;
};

// 获取用户角色对应的默认路由
export const getUserDefaultRoute = (userType: string): string => {
  return ROLE_ROUTES[userType as UserRole] || '/dashboard';
};
