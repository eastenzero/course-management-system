# 基于Python的校园课程表管理工具 - 技术文档与AI提示词

## 一、技术栈分析

### 1.1 前端技术栈
- **框架**: React 18.x + TypeScript
- **UI组件库**: Ant Design 5.x
- **状态管理**: Redux Toolkit + RTK Query
- **路由管理**: React Router v6
- **图表可视化**: ECharts + React-ECharts
- **样式方案**: Styled-Components + CSS Modules
- **构建工具**: Vite 4.x
- **代码规范**: ESLint + Prettier + Husky

### 1.2 后端技术栈
- **核心框架**: Django 4.2 + Django REST Framework
- **数据库**: PostgreSQL 15.x (主库) + Redis 7.x (缓存)
- **ORM**: Django ORM
- **认证授权**: Django-allauth + JWT
- **任务队列**: Celery + Redis
- **API文档**: Django-spectacular (OpenAPI 3.0)
- **文件存储**: Django-storages + 阿里云OSS
- **日志系统**: Django-logging + ELK Stack

### 1.3 部署与运维
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx 1.24
- **WSGI服务器**: Gunicorn
- **进程管理**: Supervisor
- **监控**: Prometheus + Grafana
- **CI/CD**: GitHub Actions

### 1.4 开发工具
- **版本控制**: Git + GitHub
- **API测试**: Postman + pytest
- **数据库管理**: pgAdmin 4
- **代码编辑器**: VS Code + PyCharm

## 二、系统架构设计

### 2.1 整体架构
```
前端层 (React SPA)
    ↓
API网关层 (Nginx + Django)
    ↓
业务逻辑层 (Django Views + Services)
    ↓
数据访问层 (Django ORM)
    ↓
数据存储层 (PostgreSQL + Redis)
```

### 2.2 核心模块划分
1. **用户管理模块** (User Management)
2. **课程管理模块** (Course Management)
3. **排课算法模块** (Scheduling Algorithm)
4. **冲突检测模块** (Conflict Detection)
5. **数据可视化模块** (Data Visualization)
6. **权限控制模块** (Permission Control)
7. **数据导入导出模块** (Data Import/Export)
8. **通知系统模块** (Notification System)

## 三、数据库设计

### 3.1 核心实体模型
- **用户表** (User): 学生、教师、管理员
- **课程表** (Course): 课程基本信息
- **教室表** (Classroom): 教室资源信息
- **时间段表** (TimeSlot): 时间段定义
- **课程安排表** (Schedule): 课程具体安排
- **选课记录表** (Enrollment): 学生选课记录
- **冲突记录表** (Conflict): 冲突检测记录

### 3.2 关系设计
- 用户-角色: 多对多关系
- 课程-教师: 多对多关系
- 课程-学生: 多对多关系 (通过选课记录)
- 课程安排-教室: 一对一关系
- 课程安排-时间段: 一对一关系

## 四、代码构建步骤

### 4.1 环境准备阶段
1. 系统环境配置 (Linux Ubuntu 22.04)
2. Python 3.11 环境安装
3. Node.js 18.x 环境安装
4. PostgreSQL 15.x 数据库安装
5. Redis 7.x 缓存服务安装
6. Docker 环境配置

### 4.2 后端开发阶段
1. Django项目初始化
2. 数据模型设计与迁移
3. API接口开发
4. 用户认证系统实现
5. 排课算法核心逻辑
6. 冲突检测机制
7. 单元测试编写

### 4.3 前端开发阶段
1. React项目初始化
2. 组件库搭建
3. 路由系统配置
4. 状态管理实现
5. API接口对接
6. 数据可视化实现
7. 响应式布局优化

### 4.4 集成测试阶段
1. 前后端联调
2. 功能测试
3. 性能测试
4. 安全测试
5. 兼容性测试

### 4.5 部署上线阶段
1. Docker镜像构建
2. 生产环境配置
3. 数据库迁移
4. 服务部署
5. 监控配置

## 五、前置系统环境配置提示词

### 5.1 Linux系统环境配置
```bash
# 系统更新
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
sudo apt install -y build-essential curl wget git vim

# 安装Python 3.11
sudo apt install -y python3.11 python3.11-dev python3.11-venv python3-pip

# 安装Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装PostgreSQL 15
sudo apt install -y postgresql-15 postgresql-contrib-15 postgresql-client-15

# 安装Redis
sudo apt install -y redis-server

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 5.2 Python虚拟环境配置
```bash
# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装核心依赖
pip install django==4.2.7
pip install djangorestframework==3.14.0
pip install psycopg2-binary==2.9.7
pip install redis==5.0.1
pip install celery==5.3.4
```

### 5.3 数据库配置
```sql
-- 创建数据库用户
CREATE USER course_admin WITH PASSWORD 'secure_password_123';

-- 创建数据库
CREATE DATABASE course_management_db OWNER course_admin;

-- 授权
GRANT ALL PRIVILEGES ON DATABASE course_management_db TO course_admin;
```

### 5.4 常见问题解决方案

#### 依赖冲突问题
- 使用虚拟环境隔离Python依赖
- 固定版本号避免自动升级
- 使用requirements.txt管理依赖

#### 版本不兼容问题
- 检查Python版本兼容性
- 使用pyenv管理多Python版本
- 定期更新依赖包

#### 数据库连接问题
- 检查PostgreSQL服务状态
- 验证连接参数配置
- 确认防火墙设置

#### Redis连接问题
- 检查Redis服务状态
- 验证配置文件设置
- 确认端口占用情况

## 六、模块化AI提示词设计

### 6.1 后端核心模块提示词
详见：`模块1-后端核心开发提示词.md`
- Django项目架构搭建
- 用户认证与权限系统
- RESTful API设计
- 数据模型设计
- 业务逻辑实现

### 6.2 前端界面模块提示词
详见：`模块2-前端界面开发提示词.md`
- React项目架构搭建
- 组件库设计
- 状态管理实现
- 响应式布局
- 用户体验优化

### 6.3 算法逻辑模块提示词
详见：`模块3-智能排课算法提示词.md`
- 遗传算法实现
- 约束条件定义
- 冲突检测机制
- 启发式算法
- 性能优化策略

### 6.4 数据生成模块提示词
详见：`模块4-测试数据生成提示词.md`
- 大规模数据生成
- 复杂场景模拟
- 数据完整性验证
- 多格式数据导出
- 性能测试数据

## 七、项目实施计划

### 7.1 开发阶段划分
1. **第一阶段** (2周): 环境搭建与基础架构
2. **第二阶段** (4周): 后端核心功能开发
3. **第三阶段** (4周): 前端界面开发
4. **第四阶段** (3周): 算法实现与优化
5. **第五阶段** (2周): 系统集成与测试
6. **第六阶段** (1周): 部署与上线

### 7.2 质量保证措施
- 代码审查制度
- 自动化测试
- 持续集成/持续部署
- 性能监控
- 安全审计

### 7.3 风险控制
- 技术风险评估
- 进度风险管控
- 质量风险预防
- 资源风险应对

## 八、技术创新点

### 8.1 智能排课算法
- 多目标优化遗传算法
- 动态约束处理机制
- 实时冲突检测
- 增量式排课更新

### 8.2 用户体验优化
- 拖拽式课程表编辑
- 实时协作功能
- 智能推荐系统
- 移动端适配

### 8.3 系统架构优势
- 微服务架构设计
- 容器化部署
- 弹性扩展能力
- 高可用性保障

---

*本技术文档为校园课程表管理工具的完整开发指南，包含详细的技术栈选择、架构设计、开发规范和实施计划。配套的模块化AI提示词文件提供了具体的开发指导。*
