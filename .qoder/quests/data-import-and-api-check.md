# 数据导入与API对接检查设计文档

## 概述

本文档描述了校园课程表管理系统的数据导入流程和API对接验证方案，确保生成的测试数据能够成功导入到Django数据库中，并通过前端展示实际数据效果。

## 系统架构

### 数据流架构

```mermaid
graph TB
    A[数据生成器] --> B[JSON数据文件]
    B --> C[数据导入脚本]
    C --> D[Django数据库]
    D --> E[Django REST API]
    E --> F[前端应用]
    F --> G[用户界面展示]
    
    subgraph "数据层"
        B
        D
    end
    
    subgraph "应用层"
        C
        E
    end
    
    subgraph "展示层"
        F
        G
    end
```

### 核心组件

| 组件 | 功能 | 技术栈 |
|------|------|--------|
| 数据生成器 | 生成测试数据 | Python |
| 数据导入脚本 | 数据适配与导入 | Django ORM |
| Django API | 提供RESTful接口 | Django REST Framework |
| 前端应用 | 数据展示界面 | React + RTK Query |

## 数据导入方案

### 数据源分析

系统支持多个规模的数据集导入：

```mermaid
classDiagram
    class DataSet {
        +scale: string
        +departments: number
        +majors: number
        +students: number
        +teachers: number
        +courses: number
    }
    
    class SmallDataSet {
        +scale: "small"
        +departments: 5
        +students: 500
        +teachers: 50
        +courses: 100
    }
    
    class MediumDataSet {
        +scale: "medium"
        +departments: 10
        +students: 5000
        +teachers: 500
        +courses: 1000
    }
    
    class LargeDataSet {
        +scale: "large"
        +departments: 20
        +students: 25000
        +teachers: 1500
        +courses: 3000
    }
    
    DataSet <|-- SmallDataSet
    DataSet <|-- MediumDataSet
    DataSet <|-- LargeDataSet
```

### 导入流程设计

```mermaid
sequenceDiagram
    participant DG as 数据生成器
    participant IS as 导入脚本
    participant DB as 数据库
    participant API as Django API
    participant FE as 前端
    
    DG->>IS: 加载JSON数据文件
    IS->>IS: 数据格式验证
    IS->>DB: 批量导入用户数据
    IS->>DB: 批量导入课程数据
    IS->>DB: 批量导入选课数据
    DB-->>IS: 导入结果反馈
    IS->>API: 触发索引重建
    API-->>IS: 确认完成
    FE->>API: 请求数据列表
    API->>DB: 查询数据
    DB-->>API: 返回数据
    API-->>FE: 返回JSON响应
    FE->>FE: 渲染数据表格
```

### 数据映射策略

#### 用户数据映射

| 生成器字段 | Django模型字段 | 转换规则 |
|-----------|---------------|----------|
| student_id | User.student_id | 直接映射 |
| name | User.first_name + last_name | 姓名分割 |
| department_id | User.department | 院系名称映射 |
| major_id | StudentProfile.major | 专业名称映射 |
| gpa | StudentProfile.gpa | Decimal转换 |

#### 课程数据映射

| 生成器字段 | Django模型字段 | 转换规则 |
|-----------|---------------|----------|
| course_id | Course.code | 课程编码生成 |
| course_name | Course.name | 直接映射 |
| credits | Course.credits | 整数转换 |
| teacher_id | Course.teacher | 外键关联 |
| semester | Course.semester | 学期格式化 |

## API接口检查方案

### 接口测试架构

```mermaid
graph TD
    A[API测试脚本] --> B[认证测试]
    A --> C[用户接口测试]
    A --> D[课程接口测试]
    A --> E[选课接口测试]
    A --> F[教室接口测试]
    A --> G[时间段接口测试]
    
    B --> H[JWT令牌验证]
    C --> I[用户列表/详情]
    D --> J[课程CRUD操作]
    E --> K[选课关系管理]
    F --> L[教室资源管理]
    G --> M[时间段配置]
    
    H --> N[测试结果报告]
    I --> N
    J --> N
    K --> N
    L --> N
    M --> N
```

### 核心API端点

#### 认证API

```http
POST /api/v1/users/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

#### 用户管理API

```http
GET /api/v1/users/profile/
Authorization: Bearer {access_token}

GET /api/v1/users/students/
Authorization: Bearer {access_token}

GET /api/v1/users/teachers/
Authorization: Bearer {access_token}
```

#### 课程管理API

```http
GET /api/v1/courses/
Authorization: Bearer {access_token}

POST /api/v1/courses/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "code": "CS101",
  "name": "计算机科学导论",
  "credits": 3,
  "hours": 48,
  "department": "计算机学院"
}
```

### 数据验证策略

```mermaid
flowchart TD
    A[开始API测试] --> B[身份认证]
    B --> C{认证成功?}
    C -->|否| D[终止测试]
    C -->|是| E[获取用户列表]
    E --> F{数据量检查}
    F -->|数据为空| G[报告数据问题]
    F -->|数据正常| H[测试课程接口]
    H --> I[测试选课接口]
    I --> J[测试教室接口]
    J --> K[生成测试报告]
    K --> L[结束]
    
    D --> M[错误日志]
    G --> M
    M --> L
```

## 前端数据展示方案

### 组件架构

```mermaid
classDiagram
    class DataDisplayContainer {
        +state: {loading, data, error}
        +useApi(): APIHook
        +render(): JSX
    }
    
    class StudentListComponent {
        +props: {students, pagination}
        +handlePageChange(): void
        +handleSearch(): void
        +render(): JSX
    }
    
    class CourseListComponent {
        +props: {courses, filters}
        +handleFilter(): void
        +handleSort(): void
        +render(): JSX
    }
    
    class DataTable {
        +props: {columns, data, actions}
        +handleEdit(): void
        +handleDelete(): void
        +render(): JSX
    }
    
    DataDisplayContainer --> StudentListComponent
    DataDisplayContainer --> CourseListComponent
    StudentListComponent --> DataTable
    CourseListComponent --> DataTable
```

### 状态管理

```mermaid
stateDiagram-v2
    [*] --> Loading
    Loading --> DataLoaded: API请求成功
    Loading --> Error: API请求失败
    DataLoaded --> Refreshing: 刷新数据
    DataLoaded --> Filtering: 应用过滤器
    DataLoaded --> Paginating: 分页导航
    Refreshing --> DataLoaded: 刷新完成
    Filtering --> DataLoaded: 过滤完成
    Paginating --> DataLoaded: 分页完成
    Error --> Loading: 重试请求
```

### 数据展示界面

#### 学生管理界面

| 字段 | 显示名称 | 数据源 |
|------|----------|--------|
| student_id | 学号 | User.student_id |
| name | 姓名 | User.first_name + last_name |
| department | 院系 | User.department |
| major | 专业 | StudentProfile.major |
| gpa | 绩点 | StudentProfile.gpa |
| enrollment_status | 状态 | StudentProfile.enrollment_status |

#### 课程管理界面

| 字段 | 显示名称 | 数据源 |
|------|----------|--------|
| code | 课程编码 | Course.code |
| name | 课程名称 | Course.name |
| credits | 学分 | Course.credits |
| teacher | 授课教师 | Course.teacher.name |
| department | 开课院系 | Course.department |
| semester | 开课学期 | Course.semester |

## 实施流程

### 阶段一：数据导入准备

```mermaid
gantt
    title 数据导入实施计划
    dateFormat  YYYY-MM-DD
    section 准备阶段
    环境检查           :done, env-check, 2024-01-01, 1d
    依赖安装           :done, deps, after env-check, 1d
    数据文件验证       :active, data-validate, after deps, 1d
    
    section 导入阶段
    小规模数据导入     :import-small, after data-validate, 1d
    API接口测试       :api-test, after import-small, 1d
    前端数据展示      :frontend-test, after api-test, 1d
    
    section 扩展阶段
    中等规模数据导入   :import-medium, after frontend-test, 1d
    大规模数据导入     :import-large, after import-medium, 1d
    性能优化          :optimize, after import-large, 1d
```

### 阶段二：API接口验证

1. **认证接口测试**
   - 用户登录功能
   - JWT令牌验证
   - 权限检查

2. **数据接口测试**
   - 用户列表接口
   - 课程列表接口
   - 选课关系接口

3. **CRUD操作测试**
   - 创建数据
   - 读取数据
   - 更新数据
   - 删除数据

### 阶段三：前端数据展示

1. **界面功能验证**
   - 数据表格显示
   - 分页功能
   - 搜索过滤
   - 排序功能

2. **用户体验测试**
   - 加载性能
   - 响应速度
   - 错误处理
   - 界面友好性

## 测试策略

### 单元测试

```python
class DataImportTestCase(TestCase):
    def test_student_data_import(self):
        """测试学生数据导入"""
        # 准备测试数据
        # 执行导入操作
        # 验证导入结果
        
    def test_course_data_import(self):
        """测试课程数据导入"""
        # 准备测试数据
        # 执行导入操作
        # 验证导入结果
```

### 集成测试

```python
class APIIntegrationTestCase(TestCase):
    def test_api_authentication(self):
        """测试API认证流程"""
        
    def test_data_retrieval(self):
        """测试数据获取流程"""
        
    def test_frontend_display(self):
        """测试前端数据展示"""
```

## 性能优化

### 数据库优化

1. **批量操作**
   - 使用bulk_create减少数据库连接
   - 批量更新优化性能

2. **索引优化**
   - 为常用查询字段添加索引
   - 复合索引优化复杂查询

3. **查询优化**
   - 使用select_related减少查询次数
   - 分页查询避免大量数据加载

### API性能优化

1. **缓存策略**
   - Redis缓存常用数据
   - API响应缓存

2. **分页机制**
   - 合理的分页大小
   - 游标分页优化

3. **响应优化**
   - 数据压缩
   - 字段筛选

### 前端性能优化

1. **数据加载优化**
   - 懒加载大量数据
   - 虚拟滚动处理长列表

2. **状态管理优化**
   - RTK Query缓存机制
   - 智能数据更新

3. **渲染优化**
   - React.memo防止不必要渲染
   - 组件代码分割

## 错误处理

### 数据导入错误

```python
class DataImportError(Exception):
    """数据导入异常"""
    pass

def handle_import_error(error):
    """处理导入错误"""
    if isinstance(error, ValidationError):
        # 数据验证错误
        return {"error": "数据格式错误", "details": str(error)}
    elif isinstance(error, IntegrityError):
        # 数据完整性错误
        return {"error": "数据约束冲突", "details": str(error)}
    else:
        # 其他错误
        return {"error": "导入失败", "details": str(error)}
```

### API错误处理

```python
class APIErrorHandler:
    @staticmethod
    def handle_authentication_error():
        """处理认证错误"""
        return {"error": "认证失败", "code": 401}
    
    @staticmethod
    def handle_permission_error():
        """处理权限错误"""
        return {"error": "权限不足", "code": 403}
    
    @staticmethod
    def handle_not_found_error():
        """处理资源不存在错误"""
        return {"error": "资源不存在", "code": 404}
```

### 前端错误处理

```typescript
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class DataDisplayErrorBoundary extends Component<Props, ErrorBoundaryState> {
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('数据展示错误:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    
    return this.props.children;
  }
}
```

## 监控与日志

### 导入监控

```python
class ImportMonitor:
    def __init__(self):
        self.logger = logging.getLogger('data_import')
    
    def log_import_start(self, data_type, count):
        """记录导入开始"""
        self.logger.info(f"开始导入{data_type}数据，共{count}条记录")
    
    def log_import_progress(self, processed, total):
        """记录导入进度"""
        progress = (processed / total) * 100
        self.logger.info(f"导入进度: {progress:.1f}% ({processed}/{total})")
    
    def log_import_complete(self, success_count, error_count):
        """记录导入完成"""
        self.logger.info(f"导入完成: 成功{success_count}条，失败{error_count}条")
```

### API监控

```python
class APIMonitor:
    def log_api_request(self, endpoint, method, user):
        """记录API请求"""
        
    def log_api_response(self, endpoint, status_code, response_time):
        """记录API响应"""
        
    def log_api_error(self, endpoint, error):
        """记录API错误"""
```

## 部署考虑

### Docker部署

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/coursedb
      - REDIS_URL=redis://redis:16379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=coursedb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:6-alpine
    ports:
      - "16379:6379"

volumes:
  postgres_data:
```

### 环境配置

```bash
# 环境变量配置
export DJANGO_SETTINGS_MODULE=course_management.settings.production
export DATABASE_URL=postgresql://user:pass@localhost:5432/coursedb
export REDIS_URL=redis://localhost:16379/0
export SECRET_KEY=your-secret-key
export DEBUG=False
```