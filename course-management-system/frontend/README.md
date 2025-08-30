# 校园课程表管理系统 - 前端

基于 React 18 + TypeScript + Ant Design 5 构建的现代化前端应用。

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite 4
- **UI组件库**: Ant Design 5
- **状态管理**: Redux Toolkit + RTK Query
- **路由**: React Router v6
- **样式**: CSS Modules + Styled Components
- **图表**: ECharts + React-ECharts
- **代码规范**: ESLint + Prettier

## 项目结构

```
src/
├── components/           # 通用组件
│   ├── common/          # 基础组件
│   ├── layout/          # 布局组件
│   └── business/        # 业务组件
├── pages/               # 页面组件
│   ├── auth/           # 认证相关页面
│   ├── dashboard/      # 仪表板
│   ├── courses/        # 课程管理
│   ├── schedules/      # 课程表管理
│   └── analytics/      # 数据分析
├── store/              # 状态管理
│   ├── slices/         # Redux切片
│   └── api/            # API切片
├── hooks/              # 自定义Hooks
├── utils/              # 工具函数
├── types/              # TypeScript类型定义
├── styles/             # 样式文件
└── assets/             # 静态资源
```

## 开发指南

### 环境要求

- Node.js >= 18.0.0
- npm >= 8.0.0

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 代码检查

```bash
npm run lint
npm run lint:fix
```

### 代码格式化

```bash
npm run format
```

### 类型检查

```bash
npm run type-check
```

## 功能特性

### 已实现功能

- ✅ 项目基础架构
- ✅ 用户认证系统
- ✅ 主布局和导航
- ✅ 响应式设计
- ✅ 主题配置
- ✅ 状态管理
- ✅ API集成
- ✅ 路由保护

### 开发中功能

- 🚧 仪表板页面
- 🚧 课程管理
- 🚧 课程表管理
- 🚧 数据分析
- 🚧 用户管理
- 🚧 系统设置

### 计划功能

- 📋 智能排课算法
- 📋 冲突检测
- 📋 数据导入导出
- 📋 通知系统
- 📋 移动端适配

## 设计系统

### 色彩系统

- 主色调: #1890ff (科技蓝)
- 成功色: #52c41a (绿色)
- 警告色: #faad14 (橙色)
- 错误色: #f5222d (红色)

### 字体系统

- 标题字体: 32px/24px/20px/16px
- 正文字体: 14px
- 说明字体: 12px

### 间距系统

- 基础间距: 8px
- 标准间距: 16px
- 大间距: 24px
- 超大间距: 32px

## 开发规范

### 组件开发

1. 使用函数式组件 + Hooks
2. 组件名使用 PascalCase
3. 文件名与组件名保持一致
4. 每个组件都要有对应的类型定义

### 状态管理

1. 使用 Redux Toolkit 管理全局状态
2. 使用 RTK Query 处理 API 请求
3. 本地状态优先使用 useState

### 样式规范

1. 优先使用 Ant Design 组件
2. 自定义样式使用 CSS Modules
3. 全局样式放在 styles 目录
4. 响应式设计使用断点系统

### API 集成

1. 所有 API 请求都通过 RTK Query
2. 错误处理统一在拦截器中处理
3. 请求参数和响应数据都要有类型定义

## 部署说明

### 开发环境

```bash
npm run dev
```

访问 http://localhost:3000

### 生产环境

```bash
npm run build
npm run preview
```

构建产物在 `dist` 目录

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License
