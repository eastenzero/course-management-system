# 校园课程管理系统Docker部署专用提示词

## 项目概述

这是一个基于Django + React + PostgreSQL + Redis的全栈校园课程管理系统，具备智能排课算法、用户管理、课程管理、数据分析等功能。项目已完成Docker化配置，支持开发和生产环境的一键部署。

## 技术架构

### 后端技术栈
- **框架**: Django 4.2.7 + Django REST Framework 3.14.0
- **数据库**: PostgreSQL 13 (生产) / SQLite (开发)
- **缓存**: Redis 6
- **异步任务**: Celery 5.3.4
- **Web服务器**: Gunicorn 21.2.0
- **认证**: JWT (djangorestframework-simplejwt)

### 前端技术栈
- **框架**: React 18 + TypeScript
- **构建工具**: Vite 4
- **UI组件**: Ant Design 5
- **状态管理**: Redux Toolkit + RTK Query
- **Web服务器**: Nginx (生产环境)

### 智能排课算法
- **遗传算法**: 基于genetic包的智能排课
- **约束求解**: 硬约束和软约束管理
- **冲突检测**: 自动检测和解决排课冲突
- **启发式算法**: 贪心算法和局部搜索优化

## Docker部署配置

### 目录结构
```
course-management-system/
├── docker-compose.yml              # 开发环境配置
├── docker-compose.prod.yml         # 生产环境配置
├── backend/
│   ├── Dockerfile                  # 后端镜像构建
│   ├── docker-entrypoint.sh       # 启动脚本
│   └── requirements.txt           # Python依赖
├── frontend/
│   ├── Dockerfile                  # 前端镜像构建
│   ├── nginx.conf                 # Nginx配置
│   └── package.json              # Node.js依赖
├── deployment/docker/
│   ├── deploy.sh                  # 部署脚本
│   ├── entrypoint.sh             # 通用启动脚本
│   └── init-db.sql               # 数据库初始化
└── algorithms/                    # 智能排课算法模块
```

### 核心服务组件

#### 1. PostgreSQL数据库
```yaml
db:
  image: postgres:13-alpine
  environment:
    POSTGRES_DB: course_management
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres123}
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./deployment/docker/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
```

#### 2. Redis缓存
```yaml
redis:
  image: redis:6-alpine
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis123}
  volumes:
    - redis_data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
```

#### 3. Django后端
```yaml
backend:
  build:
    context: .
    dockerfile: ./backend/Dockerfile
  environment:
    - DEBUG=False
    - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/course_management
    - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
  volumes:
    - static_volume:/app/static
    - media_volume:/app/media
  depends_on:
    db: { condition: service_healthy }
    redis: { condition: service_healthy }
```

#### 4. React前端
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  ports:
    - "80:80"
  depends_on:
    - backend
```

## 部署步骤详解

### 快速开发环境部署

#### 1. 环境准备
```bash
# 确保安装Docker和Docker Compose
docker --version
docker-compose --version

# 克隆项目
git clone <repository-url>
cd course-management-system
```

#### 2. 环境配置
```bash
# 创建环境变量文件（可选，有默认值）
cp .env.example .env

# 编辑环境变量（使用默认值也可以正常运行）
nano .env
```

#### 3. 一键启动
```bash
# 方式1：使用部署脚本（推荐）
chmod +x deployment/docker/deploy.sh
./deployment/docker/deploy.sh dev

# 方式2：使用docker-compose直接启动
docker-compose up -d
```

#### 4. 服务验证
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 访问应用
# 前端: http://localhost
# 后端API: http://localhost:8000
# 管理后台: http://localhost:8000/admin (admin/admin123)
```

### 生产环境部署

#### 1. 环境变量配置
```bash
# 创建生产环境配置
cat > .env << EOF
# 数据库配置
DB_PASSWORD=your_secure_db_password
REDIS_PASSWORD=your_secure_redis_password

# Django配置
SECRET_KEY=your_very_long_secret_key_here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
CORS_ALLOWED_ORIGINS=https://your-domain.com

# 邮件配置（可选）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
EOF
```

#### 2. 生产部署
```bash
# 使用生产配置部署
./deployment/docker/deploy.sh prod

# 或手动启动
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. SSL配置（生产环境）
```bash
# 配置SSL证书
mkdir -p deployment/docker/nginx/ssl
# 将SSL证书文件放入该目录
# 修改nginx配置启用HTTPS
```

## 核心功能模块

### 1. 用户认证系统
- **多角色支持**: 管理员、教师、学生
- **JWT认证**: 无状态Token认证
- **权限控制**: 基于角色的权限管理
- **API端点**: `/api/v1/users/auth/`

### 2. 课程管理系统
- **课程CRUD**: 完整的课程管理功能
- **选课管理**: 学生选课和退课
- **统计分析**: 选课人数和成绩统计
- **API端点**: `/api/v1/courses/`

### 3. 智能排课系统
- **遗传算法**: 自动优化排课方案
- **约束管理**: 硬约束（必须满足）和软约束（尽量满足）
- **冲突检测**: 实时检测教师、教室、时间冲突
- **API端点**: `/api/v1/schedules/`

### 4. 教室管理系统
- **教室信息**: 容量、设备、位置管理
- **可用性查询**: 实时查询教室使用状态
- **利用率统计**: 教室使用效率分析
- **API端点**: `/api/v1/classrooms/`

### 5. 数据分析模块
- **课程统计**: 选课趋势和成绩分析
- **教师工作量**: 授课时长和课程统计
- **系统报表**: 自动生成各类报表
- **异步处理**: Celery处理复杂统计任务

## 故障排除指南

### 常见问题解决

#### 1. 端口冲突
```bash
# 查看端口占用
netstat -tlnp | grep -E '(80|8000|5432|6379)'

# 修改端口映射
# 在docker-compose.yml中修改ports配置
ports:
  - "8080:80"  # 前端改为8080端口
```

#### 2. 数据库连接失败
```bash
# 检查数据库状态
docker-compose logs db

# 重启数据库
docker-compose restart db

# 手动连接测试
docker-compose exec db psql -U postgres -d course_management
```

#### 3. 权限问题
```bash
# 给脚本执行权限
chmod +x deployment/docker/deploy.sh

# Docker权限配置
sudo usermod -aG docker $USER
# 重新登录生效
```

#### 4. 内存不足
```bash
# 清理Docker资源
docker system prune -a

# 检查资源使用
docker stats
```

### 日志分析
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# 实时跟踪日志
docker-compose logs -f backend
```

## 性能优化配置

### 1. 数据库优化
```sql
-- PostgreSQL性能调优
shared_buffers = 256MB
effective_cache_size = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

### 2. Redis缓存配置
```bash
# Redis内存优化
maxmemory 512mb
maxmemory-policy allkeys-lru
```

### 3. Nginx优化
```nginx
# 启用Gzip压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_comp_level 6;

# 静态文件缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 数据管理

### 备份策略
```bash
# 数据库备份
./deployment/docker/deploy.sh backup

# 手动备份
docker-compose exec -T db pg_dump -U postgres course_management > backup.sql
```

### 数据恢复
```bash
# 数据恢复
./deployment/docker/deploy.sh restore backup.sql

# 手动恢复
docker-compose exec -T db psql -U postgres course_management < backup.sql
```

### 初始数据
```bash
# 创建测试数据
docker-compose exec backend python create_test_data.py

# 创建超级用户
docker-compose exec backend python manage.py createsuperuser
```

## 监控和运维

### 健康检查
```bash
# 检查所有服务状态
./deployment/docker/deploy.sh status

# 手动健康检查
curl http://localhost:8000/api/health/
curl http://localhost/health
```

### 系统监控
```bash
# 查看资源使用
docker stats

# 查看容器状态
docker-compose ps

# 查看网络状态
docker network ls
docker network inspect course-management-system_course_management_network
```

## 扩展部署

### 集群部署
```yaml
# 后端服务扩展
backend:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
```

### 负载均衡
```nginx
# Nginx负载均衡配置
upstream backend_cluster {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

## 安全配置

### 生产环境安全
```bash
# 强密码配置
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 50)

# 防火墙配置
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 5432/tcp
ufw deny 6379/tcp
```

### SSL证书配置
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

## 快速命令参考

### 基础命令
```bash
# 启动开发环境
./deployment/docker/deploy.sh dev

# 启动生产环境
./deployment/docker/deploy.sh prod

# 查看服务状态
./deployment/docker/deploy.sh status

# 查看日志
./deployment/docker/deploy.sh logs

# 停止服务
./deployment/docker/deploy.sh stop

# 清理环境
./deployment/docker/deploy.sh clean

# 备份数据
./deployment/docker/deploy.sh backup

# 恢复数据
./deployment/docker/deploy.sh restore backup_file.sql
```

### Docker Compose命令
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f [service_name]

# 执行容器内命令
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python create_test_data.py

# 重新构建特定服务
docker-compose build backend
docker-compose up -d backend
```

### 开发调试命令
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库
docker-compose exec db psql -U postgres -d course_management

# 进入Redis
docker-compose exec redis redis-cli

# 查看网络
docker network ls
docker network inspect course-management-system_course_management_network

# 查看卷
docker volume ls
docker volume inspect course-management-system_postgres_data
```

## 环境变量说明

### 必需环境变量
```bash
# 数据库配置
DB_PASSWORD=postgres123                    # 数据库密码
REDIS_PASSWORD=redis123                   # Redis密码

# Django配置
SECRET_KEY=your-secret-key-here          # Django密钥
DEBUG=False                              # 调试模式
ALLOWED_HOSTS=localhost,127.0.0.1        # 允许的主机
CORS_ALLOWED_ORIGINS=http://localhost    # CORS配置
```

### 可选环境变量
```bash
# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# 超级用户配置
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

## API端点概览

### 认证相关
- `POST /api/v1/users/auth/login/` - 用户登录
- `POST /api/v1/users/auth/logout/` - 用户登出
- `GET /api/v1/users/profile/` - 获取用户信息
- `PUT /api/v1/users/profile/` - 更新用户信息

### 课程管理
- `GET /api/v1/courses/` - 课程列表
- `POST /api/v1/courses/` - 创建课程
- `GET /api/v1/courses/{id}/` - 课程详情
- `PUT /api/v1/courses/{id}/` - 更新课程
- `DELETE /api/v1/courses/{id}/` - 删除课程
- `POST /api/v1/courses/enrollments/` - 选课
- `DELETE /api/v1/courses/{id}/drop/` - 退课

### 排课管理
- `GET /api/v1/schedules/` - 课程安排列表
- `POST /api/v1/schedules/` - 创建课程安排
- `POST /api/v1/schedules/check-conflicts/` - 冲突检测
- `POST /api/v1/schedules/batch-create/` - 批量排课
- `GET /api/v1/schedules/table/` - 课程表查询

### 教室管理
- `GET /api/v1/classrooms/` - 教室列表
- `POST /api/v1/classrooms/` - 创建教室
- `GET /api/v1/classrooms/availability/` - 教室可用性查询
- `GET /api/v1/classrooms/utilization/` - 教室利用率统计

### 智能排课算法
- `POST /api/v1/algorithms/genetic-schedule/` - 遗传算法排课
- `POST /api/v1/algorithms/optimize-schedule/` - 排课优化
- `GET /api/v1/algorithms/constraints/` - 约束条件管理

### 数据分析
- `GET /api/v1/analytics/dashboard/` - 仪表板数据
- `GET /api/v1/analytics/courses/` - 课程统计
- `GET /api/v1/analytics/teachers/` - 教师工作量统计
- `GET /api/v1/analytics/classrooms/` - 教室利用率分析

## 部署检查清单

### 部署前检查
- [ ] Docker和Docker Compose已安装
- [ ] 防火墙配置正确（80, 443端口开放）
- [ ] SSL证书已配置（生产环境）
- [ ] 环境变量已设置
- [ ] 域名DNS已配置（生产环境）

### 部署后验证
- [ ] 所有容器正常运行
- [ ] 数据库连接正常
- [ ] Redis缓存正常
- [ ] 前端页面可访问
- [ ] API接口正常响应
- [ ] 管理后台可登录
- [ ] 健康检查通过

### 功能测试
- [ ] 用户注册登录功能
- [ ] 课程创建和管理
- [ ] 排课功能测试
- [ ] 冲突检测功能
- [ ] 数据统计功能
- [ ] 文件上传下载
- [ ] 通知系统（如果启用）

## 性能基准

### 推荐硬件配置

#### 开发环境
- **CPU**: 2核
- **内存**: 4GB
- **存储**: 20GB SSD
- **网络**: 10Mbps

#### 生产环境（小型）
- **CPU**: 4核
- **内存**: 8GB
- **存储**: 100GB SSD
- **网络**: 100Mbps

#### 生产环境（中型）
- **CPU**: 8核
- **内存**: 16GB
- **存储**: 500GB SSD
- **网络**: 1Gbps

### 性能指标

#### 响应时间目标
- **首页加载**: < 2秒
- **API响应**: < 500ms
- **数据库查询**: < 200ms
- **缓存命中**: < 10ms

#### 并发能力
- **开发环境**: 10并发用户
- **小型生产**: 100并发用户
- **中型生产**: 500并发用户

## 升级和维护

### 版本升级
```bash
# 备份数据
./deployment/docker/deploy.sh backup

# 拉取新代码
git pull origin main

# 重新构建和部署
docker-compose build --no-cache
docker-compose up -d

# 运行迁移
docker-compose exec backend python manage.py migrate
```

### 定期维护
```bash
# 每周执行
# 1. 数据库备份
./deployment/docker/deploy.sh backup

# 2. 清理Docker资源
docker system prune -f

# 3. 更新系统包
sudo apt update && sudo apt upgrade

# 4. 检查日志文件大小
du -sh /var/lib/docker/containers/*/
```

### 监控脚本
```bash
#!/bin/bash
# 系统监控脚本

# 检查容器状态
if ! docker-compose ps | grep -q "Up"; then
    echo "警告：有容器未正常运行"
    docker-compose ps
fi

# 检查磁盘空间
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "警告：磁盘使用率超过80%"
fi

# 检查内存使用
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "警告：内存使用率超过90%"
fi
```

## 最佳实践总结

### 开发阶段
1. **使用开发配置**: 启用DEBUG模式，使用SQLite数据库
2. **代码热重载**: 挂载代码目录到容器
3. **日志调试**: 开启详细日志输出
4. **测试数据**: 使用create_test_data.py创建测试数据

### 生产部署
1. **安全配置**: 禁用DEBUG，使用强密码
2. **性能优化**: 启用缓存，配置CDN
3. **监控告警**: 配置系统监控和告警
4. **备份策略**: 定期自动备份数据

### 运维管理
1. **版本控制**: 使用Git标签管理版本
2. **滚动更新**: 使用蓝绿部署避免停机
3. **日志管理**: 配置日志轮转和集中收集
4. **文档维护**: 保持部署文档更新

## 技术支持

### 常见问题解答
**Q: 如何重置管理员密码？**
A: `docker-compose exec backend python manage.py changepassword admin`

**Q: 如何清空数据库重新开始？**
A: `docker-compose down -v && docker-compose up -d`

**Q: 如何查看详细错误信息？**
A: `docker-compose logs backend | tail -100`

**Q: 如何扩展后端服务实例？**
A: `docker-compose up -d --scale backend=3`

### 联系方式
- **项目文档**: 查看项目根目录下的各类文档
- **日志分析**: 优先查看容器日志进行问题诊断
- **社区支持**: 查看项目README和Issues

---

**注意**: 本提示词基于项目当前状态编写，部署前请确认项目代码是最新版本，并根据实际环境调整配置参数。首次部署建议先在测试环境验证，确认无误后再部署到生产环境。