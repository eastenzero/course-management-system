# 开发指南

## 项目概述

这是一个基于React + TypeScript + Ant Design的课程管理系统前端项目，采用现代化的开发技术栈和最佳实践。

## 技术栈

### 核心技术
- **React 18** - 前端框架
- **TypeScript** - 类型安全
- **Ant Design 5** - UI组件库
- **Redux Toolkit** - 状态管理
- **React Router 6** - 路由管理
- **Axios** - HTTP客户端
- **Day.js** - 日期处理

### 开发工具
- **Vite** - 构建工具
- **ESLint** - 代码检查
- **Prettier** - 代码格式化
- **Jest** - 单元测试
- **Cypress** - 端到端测试
- **React Testing Library** - 组件测试

### 性能优化
- **React.memo** - 组件优化
- **React Window** - 虚拟滚动
- **懒加载** - 图片和组件懒加载
- **防抖** - 用户输入优化

## 项目结构

```
src/
├── components/          # 组件
│   ├── common/         # 通用组件
│   ├── business/       # 业务组件
│   └── layout/         # 布局组件
├── pages/              # 页面组件
├── hooks/              # 自定义Hooks
├── utils/              # 工具函数
├── services/           # API服务
├── store/              # Redux状态管理
├── types/              # TypeScript类型定义
├── styles/             # 样式文件
└── assets/             # 静态资源
```

## 开发环境设置

### 1. 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0 或 yarn >= 1.22.0

### 2. 安装依赖
```bash
npm install
# 或
yarn install
```

### 3. 启动开发服务器
```bash
npm run dev
# 或
yarn dev
```

### 4. 构建生产版本
```bash
npm run build
# 或
yarn build
```

## 开发规范

### 1. 代码风格
- 使用TypeScript编写所有代码
- 遵循ESLint和Prettier配置
- 使用函数式组件和Hooks
- 组件名使用PascalCase
- 文件名使用PascalCase（组件）或camelCase（工具函数）

### 2. 组件开发规范
```tsx
// 组件示例
import React, { memo } from 'react';
import { Button, Space } from 'antd';

interface MyComponentProps {
  /** 标题 */
  title: string;
  /** 是否显示 */
  visible?: boolean;
  /** 点击回调 */
  onClick?: () => void;
}

const MyComponent: React.FC<MyComponentProps> = memo(({
  title,
  visible = true,
  onClick,
}) => {
  if (!visible) return null;

  return (
    <div>
      <h2>{title}</h2>
      <Button onClick={onClick}>点击</Button>
    </div>
  );
});

MyComponent.displayName = 'MyComponent';

export default MyComponent;
```

### 3. Hooks使用规范
```tsx
// 自定义Hook示例
import { useState, useCallback } from 'react';

export function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);
  
  const toggle = useCallback(() => {
    setValue(prev => !prev);
  }, []);
  
  const setTrue = useCallback(() => {
    setValue(true);
  }, []);
  
  const setFalse = useCallback(() => {
    setValue(false);
  }, []);
  
  return { value, toggle, setTrue, setFalse };
}
```

### 4. API调用规范
```tsx
// 使用自定义useApi Hook
import { useApi } from '../hooks';
import { courseAPI } from '../services/api';

const { data, loading, run, refresh } = useApi(courseAPI.getCourses, {
  immediate: true,
  showError: true,
  onSuccess: (data) => {
    console.log('获取成功:', data);
  },
});
```

## 测试指南

### 1. 单元测试
```bash
# 运行所有测试
npm run test

# 监听模式
npm run test:watch

# 生成覆盖率报告
npm run test:coverage
```

### 2. 组件测试示例
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent title="测试标题" />);
    expect(screen.getByText('测试标题')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const mockClick = jest.fn();
    render(<MyComponent title="测试" onClick={mockClick} />);
    
    fireEvent.click(screen.getByText('点击'));
    expect(mockClick).toHaveBeenCalledTimes(1);
  });
});
```

### 3. 端到端测试
```bash
# 打开Cypress测试界面
npm run cypress:open

# 运行所有E2E测试
npm run test:e2e
```

## 性能优化指南

### 1. 组件优化
- 使用`React.memo`包装组件
- 使用`useCallback`和`useMemo`优化函数和计算
- 避免在渲染函数中创建新对象

### 2. 大数据处理
- 使用`VirtualTable`处理大量表格数据
- 使用`InfiniteList`实现无限滚动
- 使用`LazyImage`实现图片懒加载

### 3. 网络优化
- 使用防抖处理用户输入
- 实现请求缓存和重复请求取消
- 使用分页减少数据传输量

## 部署指南

### 1. 构建生产版本
```bash
npm run build
```

### 2. 预览构建结果
```bash
npm run preview
```

### 3. 环境变量配置
创建`.env.production`文件：
```
VITE_API_BASE_URL=https://api.example.com
VITE_APP_TITLE=课程管理系统
```

## 常见问题

### 1. 开发服务器启动失败
- 检查Node.js版本是否符合要求
- 删除`node_modules`重新安装依赖
- 检查端口是否被占用

### 2. 构建失败
- 运行`npm run type-check`检查TypeScript错误
- 运行`npm run lint`检查代码规范
- 检查环境变量配置

### 3. 测试失败
- 确保测试环境配置正确
- 检查Mock数据是否正确
- 查看测试覆盖率报告

## 贡献指南

### 1. 提交代码前
```bash
# 检查代码规范
npm run lint

# 运行测试
npm run test

# 格式化代码
npm run format
```

### 2. 提交信息规范
```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建工具或依赖更新
```

### 3. 分支管理
- `main` - 主分支，用于生产环境
- `develop` - 开发分支，用于集成测试
- `feature/*` - 功能分支
- `hotfix/*` - 热修复分支

## 资源链接

- [React官方文档](https://react.dev/)
- [TypeScript官方文档](https://www.typescriptlang.org/)
- [Ant Design官方文档](https://ant.design/)
- [Redux Toolkit官方文档](https://redux-toolkit.js.org/)
- [React Router官方文档](https://reactrouter.com/)
- [Jest官方文档](https://jestjs.io/)
- [Cypress官方文档](https://www.cypress.io/)

## 联系方式

如有问题或建议，请联系开发团队或提交Issue。
