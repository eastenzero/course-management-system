// 通用组件导出
export { default as BreadcrumbNav } from './BreadcrumbNav';
export { default as DataTable } from './DataTable';
export { default as ProtectedRoute } from './ProtectedRoute';
export { default as RouteErrorBoundary } from './RouteErrorBoundary';

// 新增的通用组件
export { default as EmptyState } from './EmptyState';
export type { EmptyStateProps } from './EmptyState';

export { default as LoadingSpinner, PageLoading, TableLoading, ButtonLoading, FullScreenLoading } from './LoadingSpinner';
export type { LoadingSpinnerProps } from './LoadingSpinner';

export { default as ConfirmDialog, showConfirm } from './ConfirmDialog';
export type { ConfirmDialogProps } from './ConfirmDialog';

export { default as SearchForm } from './SearchForm';
export type { SearchFormProps, SearchField } from './SearchForm';

export { default as FilterPanel } from './FilterPanel';
export type { FilterPanelProps, FilterConfig, FilterOption } from './FilterPanel';

export { default as FormBuilder } from './FormBuilder';
export type { FormBuilderProps, FormFieldConfig, FormFieldOption } from './FormBuilder';

// 性能优化组件
export { default as VirtualTable } from './VirtualTable';
export type { VirtualTableProps } from './VirtualTable';

export { default as LazyImage } from './LazyImage';
export type { LazyImageProps } from './LazyImage';

export { default as InfiniteList } from './InfiniteList';
export type { InfiniteListProps } from './InfiniteList';

export { default as OptimizedForm, withFormItemOptimization, OptimizedFormItem } from './OptimizedForm';
export type { OptimizedFormProps } from './OptimizedForm';

export { default as PerformanceMonitor } from './PerformanceMonitor';

// 动态背景
export { default as DynamicBackground } from './DynamicBackground';

// 主题选择器
export { default as ThemeSelector } from './ThemeSelector';
