# 校园课程表管理系统 - 后端模块

## 项目概述

这是一个基于Django REST Framework开发的校园课程表管理系统后端，提供完整的课程管理、排课管理、用户管理等功能。

## 技术栈

- **框架**: Django 4.2.7 + Django REST Framework 3.14.0
- **数据库**: PostgreSQL (生产环境) / SQLite (开发环境)
- **缓存**: Redis
- **异步任务**: Celery
- **认证**: JWT (Simple JWT)
- **API文档**: drf-spectacular (Swagger)
- **其他**: CORS支持、过滤器、分页等

## 项目结构

```
backend/
├── course_management/          # 项目配置
│   ├── settings.py            # 主配置文件
│   ├── urls.py               # 主路由配置
│   ├── celery.py             # Celery配置
│   └── wsgi.py               # WSGI配置
├── apps/                      # 应用模块
│   ├── users/                # 用户管理
│   ├── courses/              # 课程管理
│   ├── classrooms/           # 教室管理
│   ├── schedules/            # 排课管理
│   └── analytics/            # 数据分析
├── utils/                     # 工具模块
│   └── cache.py              # 缓存工具
├── logs/                      # 日志文件
├── media/                     # 媒体文件
├── static/                    # 静态文件
└── requirements.txt           # 依赖包
```

## 核心功能

### 1. 用户认证与权限系统

- **自定义用户模型**: 扩展Django默认用户模型，支持学生、教师、管理员等角色
- **JWT认证**: 基于Token的无状态认证
- **权限控制**: 基于角色的权限控制(RBAC)
- **API端点**:
  - `POST /api/v1/users/auth/login/` - 用户登录
  - `POST /api/v1/users/auth/logout/` - 用户登出
  - `GET /api/v1/users/profile/` - 获取用户信息
  - `PUT /api/v1/users/profile/` - 更新用户信息

### 2. 课程管理系统

- **课程CRUD**: 完整的课程增删改查功能
- **选课管理**: 学生选课、退课功能
- **课程统计**: 选课人数、成绩统计等
- **API端点**:
  - `GET /api/v1/courses/` - 课程列表
  - `POST /api/v1/courses/` - 创建课程
  - `GET /api/v1/courses/{id}/` - 课程详情
  - `POST /api/v1/courses/enrollments/` - 选课
  - `POST /api/v1/courses/{id}/drop/` - 退课

### 3. 教室管理系统

- **教学楼管理**: 教学楼信息管理
- **教室管理**: 教室信息、容量、设备管理
- **可用性查询**: 查询指定时间段教室可用性
- **利用率统计**: 教室使用率统计
- **API端点**:
  - `GET /api/v1/classrooms/` - 教室列表
  - `GET /api/v1/classrooms/availability/` - 教室可用性查询
  - `GET /api/v1/classrooms/utilization/` - 教室利用率统计

### 4. 排课管理系统

- **时间段管理**: 配置上课时间段
- **排课功能**: 创建、修改、删除课程安排
- **冲突检测**: 自动检测教师、教室时间冲突
- **批量排课**: 支持批量创建课程安排
- **课程表查询**: 学生、教师、教室课程表查询
- **API端点**:
  - `GET /api/v1/schedules/` - 课程安排列表
  - `POST /api/v1/schedules/` - 创建课程安排
  - `POST /api/v1/schedules/check-conflicts/` - 冲突检测
  - `POST /api/v1/schedules/batch-create/` - 批量排课
  - `GET /api/v1/schedules/table/` - 课程表查询

### 5. 数据分析系统

- **课程统计**: 选课统计、成绩分析
- **教室利用率**: 教室使用情况分析
- **教师工作量**: 教师授课统计
- **系统报表**: 自动生成各类统计报表
- **异步任务**: 使用Celery处理耗时统计任务

## 性能优化

### 1. 缓存策略

- **Redis缓存**: 使用Redis缓存频繁查询的数据
- **分层缓存**: 不同类型数据使用不同缓存时间
- **缓存失效**: 数据更新时自动清除相关缓存

### 2. 数据库优化

- **索引优化**: 为常用查询字段添加数据库索引
- **查询优化**: 使用select_related和prefetch_related减少查询次数
- **分页**: 大数据量查询使用分页

### 3. 异步处理

- **Celery任务**: 统计计算等耗时操作使用异步任务
- **定时任务**: 定期更新统计数据

## 安全特性

- **JWT认证**: 无状态Token认证
- **权限控制**: 细粒度的API权限控制
- **数据验证**: 严格的输入数据验证
- **CORS配置**: 跨域请求安全配置
- **密码安全**: 密码强度验证和安全存储

## API文档

项目集成了Swagger API文档，启动服务后访问：
- Swagger UI: `http://localhost:8000/api/docs/`
- API Schema: `http://localhost:8000/api/schema/`

## 部署说明

### 开发环境

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 数据库迁移：
```bash
python manage.py makemigrations
python manage.py migrate
```

3. 创建超级用户：
```bash
python manage.py createsuperuser
```

4. 启动开发服务器：
```bash
python manage.py runserver
```

### 生产环境

1. 配置环境变量：
   - `SECRET_KEY`: Django密钥
   - `DEBUG`: 设置为False
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`: 数据库配置
   - `REDIS_HOST`, `REDIS_PORT`: Redis配置

2. 收集静态文件：
```bash
python manage.py collectstatic
```

3. 启动Celery Worker：
```bash
celery -A course_management worker -l info
```

## 测试

建议为所有API端点编写单元测试和集成测试，确保系统稳定性。

## 扩展功能

系统设计具有良好的扩展性，可以轻松添加以下功能：
- 成绩管理系统
- 考试安排系统
- 通知系统
- 移动端API
- 数据导入导出
- 更复杂的排课算法

## 联系方式

如有问题或建议，请联系开发团队。
