/**
 * 路由配置验证工具
 * 用于验证路由配置的完整性和正确性
 */

import { routeConfigs, breadcrumbConfig, menuPermissions } from '../router/routes';
import type { UserRole } from '../types/index';

interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  summary: {
    totalRoutes: number;
    protectedRoutes: number;
    publicRoutes: number;
    adminOnlyRoutes: number;
    teacherRoutes: number;
    studentRoutes: number;
  };
}

/**
 * 验证路由配置
 */
export const validateRouteConfig = (): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // 统计信息
  let totalRoutes = 0;
  let protectedRoutes = 0;
  let publicRoutes = 0;
  let adminOnlyRoutes = 0;
  let teacherRoutes = 0;
  let studentRoutes = 0;

  // 验证路由配置
  routeConfigs.forEach((config, index) => {
    totalRoutes++;
    
    // 检查路径格式
    if (!config.path.startsWith('/')) {
      errors.push(`Route ${index}: Path should start with '/' - ${config.path}`);
    }
    
    // 检查角色配置
    if (config.roles && config.roles.length > 0) {
      protectedRoutes++;
      
      // 统计角色分布
      if (config.roles.includes('admin')) adminOnlyRoutes++;
      if (config.roles.includes('teacher')) teacherRoutes++;
      if (config.roles.includes('student')) studentRoutes++;
      
      // 检查角色有效性
      const validRoles: UserRole[] = ['admin', 'teacher', 'student'];
      config.roles.forEach(role => {
        if (!validRoles.includes(role)) {
          errors.push(`Route ${config.path}: Invalid role '${role}'`);
        }
      });
    } else {
      publicRoutes++;
      warnings.push(`Route ${config.path}: No roles specified, route is public`);
    }
    
    // 检查元素是否存在
    if (!config.element) {
      errors.push(`Route ${config.path}: Missing element`);
    }
  });

  // 验证面包屑配置
  const routePaths = routeConfigs.map(config => config.path.replace('/*', ''));
  Object.keys(breadcrumbConfig).forEach(breadcrumbPath => {
    const matchingRoute = routePaths.find(routePath => 
      breadcrumbPath.startsWith(routePath.replace('/*', ''))
    );
    
    if (!matchingRoute) {
      warnings.push(`Breadcrumb path '${breadcrumbPath}' has no matching route`);
    }
  });

  // 验证菜单权限配置
  Object.keys(menuPermissions).forEach(menuPath => {
    const matchingRoute = routePaths.find(routePath => 
      menuPath.startsWith(routePath.replace('/*', ''))
    );
    
    if (!matchingRoute) {
      warnings.push(`Menu permission path '${menuPath}' has no matching route`);
    }
  });

  // 检查是否有重复路径
  const pathCounts = new Map<string, number>();
  routeConfigs.forEach(config => {
    const count = pathCounts.get(config.path) || 0;
    pathCounts.set(config.path, count + 1);
  });
  
  pathCounts.forEach((count, path) => {
    if (count > 1) {
      errors.push(`Duplicate route path: ${path} (appears ${count} times)`);
    }
  });

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    summary: {
      totalRoutes,
      protectedRoutes,
      publicRoutes,
      adminOnlyRoutes,
      teacherRoutes,
      studentRoutes,
    },
  };
};

/**
 * 验证用户权限覆盖率
 */
export const validatePermissionCoverage = (): {
  admin: string[];
  teacher: string[];
  student: string[];
  uncovered: string[];
} => {
  const allPaths = Object.keys(menuPermissions);
  
  const adminPaths = allPaths.filter(path => 
    menuPermissions[path].includes('admin')
  );
  
  const teacherPaths = allPaths.filter(path => 
    menuPermissions[path].includes('teacher')
  );
  
  const studentPaths = allPaths.filter(path => 
    menuPermissions[path].includes('student')
  );
  
  const coveredPaths = new Set([...adminPaths, ...teacherPaths, ...studentPaths]);
  const uncovered = allPaths.filter(path => !coveredPaths.has(path));
  
  return {
    admin: adminPaths,
    teacher: teacherPaths,
    student: studentPaths,
    uncovered,
  };
};

/**
 * 生成路由报告
 */
export const generateRouteReport = (): string => {
  const validation = validateRouteConfig();
  const coverage = validatePermissionCoverage();
  
  let report = '# 路由配置报告\n\n';
  
  // 基本统计
  report += '## 基本统计\n\n';
  report += `- 总路由数: ${validation.summary.totalRoutes}\n`;
  report += `- 受保护路由: ${validation.summary.protectedRoutes}\n`;
  report += `- 公开路由: ${validation.summary.publicRoutes}\n`;
  report += `- 管理员专用路由: ${validation.summary.adminOnlyRoutes}\n`;
  report += `- 教师可访问路由: ${validation.summary.teacherRoutes}\n`;
  report += `- 学生可访问路由: ${validation.summary.studentRoutes}\n\n`;
  
  // 验证结果
  report += '## 验证结果\n\n';
  report += `配置有效性: ${validation.isValid ? '✅ 有效' : '❌ 无效'}\n\n`;
  
  if (validation.errors.length > 0) {
    report += '### 错误\n\n';
    validation.errors.forEach(error => {
      report += `- ❌ ${error}\n`;
    });
    report += '\n';
  }
  
  if (validation.warnings.length > 0) {
    report += '### 警告\n\n';
    validation.warnings.forEach(warning => {
      report += `- ⚠️ ${warning}\n`;
    });
    report += '\n';
  }
  
  // 权限覆盖率
  report += '## 权限覆盖率\n\n';
  report += `### 管理员 (${coverage.admin.length} 个路由)\n`;
  coverage.admin.forEach(path => {
    report += `- ${path}\n`;
  });
  
  report += `\n### 教师 (${coverage.teacher.length} 个路由)\n`;
  coverage.teacher.forEach(path => {
    report += `- ${path}\n`;
  });
  
  report += `\n### 学生 (${coverage.student.length} 个路由)\n`;
  coverage.student.forEach(path => {
    report += `- ${path}\n`;
  });
  
  if (coverage.uncovered.length > 0) {
    report += `\n### 未覆盖的路由 (${coverage.uncovered.length} 个)\n`;
    coverage.uncovered.forEach(path => {
      report += `- ${path}\n`;
    });
  }
  
  return report;
};

/**
 * 在开发环境下打印路由报告
 */
export const printRouteReport = (): void => {
  if (process.env.NODE_ENV === 'development') {
    console.group('🛣️ 路由配置报告');
    console.log(generateRouteReport());
    console.groupEnd();
  }
};
