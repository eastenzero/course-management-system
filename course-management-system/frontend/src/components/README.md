# 组件库使用文档

## 概述

本项目包含了一套完整的React组件库，分为通用组件、业务组件和布局组件三大类。所有组件都使用TypeScript编写，提供完整的类型定义。

## 组件分类

### 通用组件 (Common Components)

#### 1. 数据展示组件

**EmptyState** - 空状态组件
```tsx
import { EmptyState } from '../../components/common';

<EmptyState
  type="search"
  title="没有找到数据"
  description="请尝试调整搜索条件"
  primaryAction={{
    text: '添加数据',
    onClick: () => console.log('添加'),
    icon: <PlusOutlined />,
  }}
/>
```

**LoadingSpinner** - 加载动画组件
```tsx
import { LoadingSpinner, PageLoading, TableLoading } from '../../components/common';

// 基础用法
<LoadingSpinner loading={true} tip="加载中..." />

// 预设组件
<PageLoading tip="页面加载中..." />
<TableLoading tip="数据加载中..." />
```

**LazyImage** - 懒加载图片组件
```tsx
import { LazyImage } from '../../components/common';

<LazyImage
  src="https://example.com/image.jpg"
  placeholder="data:image/svg+xml;base64,..."
  lazy={true}
  rootMargin="50px"
  style={{ width: 200, height: 200 }}
/>
```

#### 2. 表单组件

**SearchForm** - 搜索表单组件
```tsx
import { SearchForm } from '../../components/common';

const searchFields = [
  {
    name: 'keyword',
    label: '关键词',
    type: 'input',
    placeholder: '请输入关键词',
  },
  {
    name: 'category',
    label: '分类',
    type: 'select',
    options: [
      { label: '分类1', value: 'cat1' },
      { label: '分类2', value: 'cat2' },
    ],
  },
];

<SearchForm
  fields={searchFields}
  onSearch={(values) => console.log('搜索:', values)}
  onReset={() => console.log('重置')}
/>
```

**FormBuilder** - 动态表单构建器
```tsx
import { FormBuilder } from '../../components/common';

const formFields = [
  {
    name: 'name',
    label: '姓名',
    type: 'input',
    rules: [{ required: true, message: '请输入姓名' }],
  },
  {
    name: 'email',
    label: '邮箱',
    type: 'input',
    rules: [{ type: 'email', message: '请输入有效邮箱' }],
  },
];

<FormBuilder
  fields={formFields}
  onFinish={(values) => console.log('提交:', values)}
  showSubmit={true}
  submitText="保存"
/>
```

**OptimizedForm** - 优化表单组件
```tsx
import { OptimizedForm } from '../../components/common';

<OptimizedForm
  formKey="user-form"
  enablePersist={true}
  debounceDelay={300}
  autoSave={true}
  onDebouncedValuesChange={(changed, all) => console.log('值变化:', changed)}
>
  {/* 表单项 */}
</OptimizedForm>
```

#### 3. 数据表格组件

**VirtualTable** - 虚拟滚动表格
```tsx
import { VirtualTable } from '../../components/common';

<VirtualTable
  columns={columns}
  dataSource={largeDataset}
  height={400}
  virtual={true}
  virtualThreshold={100}
  itemHeight={54}
/>
```

**InfiniteList** - 无限滚动列表
```tsx
import { InfiniteList } from '../../components/common';

<InfiniteList
  dataSource={[]}
  loadMore={async (page) => {
    const response = await api.getData({ page });
    return {
      data: response.data,
      total: response.total,
      hasMore: response.hasMore,
    };
  }}
  renderItem={(item, index) => <div>{item.name}</div>}
  height={400}
/>
```

#### 4. 交互组件

**ConfirmDialog** - 确认对话框
```tsx
import { ConfirmDialog } from '../../components/common';

<ConfirmDialog
  visible={visible}
  onClose={() => setVisible(false)}
  onConfirm={async () => {
    await deleteItem();
  }}
  title="删除确认"
  content="确定要删除这个项目吗？"
  type="warning"
  okType="danger"
/>
```

**FilterPanel** - 筛选面板
```tsx
import { FilterPanel } from '../../components/common';

const filterConfigs = [
  {
    name: 'status',
    title: '状态',
    type: 'radio',
    options: [
      { label: '全部', value: '' },
      { label: '启用', value: 'active' },
      { label: '禁用', value: 'inactive' },
    ],
  },
];

<FilterPanel
  filters={filterConfigs}
  onChange={(values) => console.log('筛选:', values)}
  title="筛选条件"
/>
```

#### 5. 性能监控组件

**PerformanceMonitor** - 性能监控组件
```tsx
import { PerformanceMonitor } from '../../components/common';

<PerformanceMonitor
  enabled={process.env.NODE_ENV === 'development'}
  showFloatingButton={true}
  onMetricsUpdate={(metrics) => console.log('性能指标:', metrics)}
/>
```

### 业务组件 (Business Components)

#### CourseCard - 课程卡片
```tsx
import { CourseCard } from '../../components/business';

<CourseCard
  course={courseData}
  showActions={true}
  onEdit={(course) => console.log('编辑:', course)}
  onView={(course) => console.log('查看:', course)}
/>
```

#### UserAvatar - 用户头像
```tsx
import { UserAvatar } from '../../components/business';

<UserAvatar
  user={userData}
  size="large"
  showName={true}
  onClick={(user) => console.log('点击用户:', user)}
/>
```

#### TimeSlotPicker - 时间段选择器
```tsx
import { TimeSlotPicker } from '../../components/business';

<TimeSlotPicker
  value={selectedTimeSlots}
  onChange={(slots) => setSelectedTimeSlots(slots)}
  weekdays={['周一', '周二', '周三', '周四', '周五']}
  timeSlots={['08:00-09:50', '10:10-12:00', '14:00-15:50']}
/>
```

## 自定义Hooks

### 1. API相关Hooks

**useApi** - API调用Hook
```tsx
import { useApi } from '../../hooks';

const { data, loading, run, refresh } = useApi(api.getUsers, {
  immediate: true,
  showError: true,
  onSuccess: (data) => console.log('成功:', data),
});
```

**usePaginatedApi** - 分页API Hook
```tsx
import { usePaginatedApi } from '../../hooks';

const { data, loading, pagination, changePage } = usePaginatedApi(api.getUsers, {
  defaultPageSize: 20,
});
```

### 2. 表单相关Hooks

**useDebounce** - 防抖Hook
```tsx
import { useDebounce, useDebouncedInput } from '../../hooks';

const debouncedValue = useDebounce(inputValue, 300);

const { value, debouncedValue, onChange } = useDebouncedInput('', 300, (value) => {
  console.log('防抖后的值:', value);
});
```

**useLocalStorage** - 本地存储Hook
```tsx
import { useLocalStorage, useUserPreference } from '../../hooks';

const [value, setValue, removeValue] = useLocalStorage('key', 'defaultValue');

const { preference, updatePreference } = useUserPreference('theme', { mode: 'light' });
```

### 3. 权限相关Hooks

**usePermission** - 权限检查Hook
```tsx
import { usePermission } from '../../hooks';

const { hasPermission, isAdmin, userRole } = usePermission();

if (hasPermission('user.create')) {
  // 显示创建按钮
}
```

## 工具函数

### 1. 格式化工具
```tsx
import { formatNumber, formatCurrency, formatTime } from '../../utils';

formatNumber(1234.56, 2); // "1,234.56"
formatCurrency(1234.56); // "¥1,234.56"
formatTime(new Date(), 'YYYY-MM-DD'); // "2024-01-01"
```

### 2. 验证工具
```tsx
import { validateEmail, validatePhone, validate } from '../../utils';

validateEmail('test@example.com'); // true
validatePhone('13800138000'); // true

const result = validate(value, [
  required('此字段必填'),
  minLength(6, '最少6位'),
]);
```

### 3. 导出工具
```tsx
import { exportToCSV, exportCourses } from '../../utils';

exportToCSV(data, headers, 'courses.csv');
exportCourses(courseList, 'excel');
```

## 最佳实践

### 1. 性能优化
- 使用 `React.memo` 包装组件避免不必要的重渲染
- 大数据列表使用 `VirtualTable` 或 `InfiniteList`
- 图片使用 `LazyImage` 实现懒加载
- 表单使用 `OptimizedForm` 实现防抖和持久化

### 2. 用户体验
- 使用 `LoadingSpinner` 显示加载状态
- 使用 `EmptyState` 处理空数据状态
- 使用 `ConfirmDialog` 确认危险操作
- 使用 `SearchForm` 和 `FilterPanel` 提供搜索筛选功能

### 3. 代码组织
- 通用组件放在 `components/common`
- 业务组件放在 `components/business`
- 自定义Hooks放在 `hooks`
- 工具函数放在 `utils`

### 4. 类型安全
- 所有组件都提供完整的TypeScript类型定义
- 使用泛型支持不同的数据类型
- 导出类型定义供外部使用

## 开发指南

### 1. 添加新组件
1. 在对应目录创建组件文件
2. 编写组件实现和类型定义
3. 添加到对应的 `index.ts` 文件中导出
4. 编写使用示例和文档

### 2. 性能考虑
- 使用 `React.memo` 优化组件
- 使用 `useCallback` 和 `useMemo` 优化函数和计算
- 避免在渲染函数中创建新对象
- 合理使用懒加载和虚拟滚动

### 3. 测试
- 为组件编写单元测试
- 测试不同的props组合
- 测试用户交互行为
- 测试错误边界情况
