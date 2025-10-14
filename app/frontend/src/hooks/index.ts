// 自定义Hooks导出
export { useRouteGuard, usePagePermission, useMenuPermission } from './useRouteGuard';

// API相关Hooks
export { useApi, usePaginatedApi } from './useApi';
export type { UseApiOptions, UseApiResult } from './useApi';

// 防抖相关Hooks
export { 
  useDebounce, 
  useDebouncedCallback, 
  useDebouncedSearch, 
  useDebouncedState, 
  useDebouncedInput 
} from './useDebounce';

// 存储相关Hooks
export { 
  useLocalStorage, 
  useSessionStorage, 
  useStorageState, 
  useUserPreference, 
  usePersistedForm 
} from './useLocalStorage';

// 分页相关Hooks
export { 
  usePagination, 
  useTablePagination, 
  useInfiniteScroll 
} from './usePagination';
export type { PaginationConfig, UsePaginationResult } from './usePagination';

// 权限相关Hooks
export { 
  usePermission, 
  usePermissionWrapper, 
  useRoutePermission 
} from './usePermission';
export type { Permission } from './usePermission';
export { PERMISSIONS } from './usePermission';
