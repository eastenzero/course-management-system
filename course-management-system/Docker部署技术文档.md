# 课程管理系统 Docker 部署技术文档

## 📋 概述

本文档详细介绍如何使用 Docker 和 Docker Compose 部署课程管理系统。系统采用微服务架构，包含前端、后端、数据库和缓存服务。

## 🏗️ 架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)       │    │   (Django)      │    │ (PostgreSQL)    │
│   Port: 80      │◄──►│   Port: 8000    │◄──►│   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │              ┌─────────────────┐
         │                       └─────────────►│     Redis       │
         │                                      │   (Cache)       │
         │                                      │   Port: 6379    │
         │                                      └─────────────────┘
         │
┌─────────────────┐
│     Nginx       │
│ (Load Balancer) │
│   Port: 8080    │
└─────────────────┘
```

## 🛠️ 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **操作系统**: Linux/macOS/Windows

### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 50GB SSD
- **网络**: 稳定的互联网连接

### 软件要求
- Docker 20.10+
- Docker Compose 2.0+
- Git

## 📦 项目结构

```
course-management-system/
├── backend/
│   ├── Dockerfile              # 后端Docker配置
│   ├── requirements.txt        # Python依赖
│   └── ...
├── frontend/
│   ├── Dockerfile              # 前端Docker配置
│   ├── nginx.conf              # Nginx配置
│   ├── package.json            # Node.js依赖
│   └── ...
├── deployment/
│   └── docker/
│       ├── deploy.sh           # 部署脚本
│       ├── init-db.sql         # 数据库初始化
│       └── nginx.conf          # 负载均衡配置
├── docker-compose.yml          # Docker Compose配置
├── .env.example                # 环境变量模板
└── Docker部署技术文档.md       # 本文档
```

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd course-management-system
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（重要！）
nano .env
```

### 3. 一键部署开发环境
```bash
# 使用部署脚本
./deployment/docker/deploy.sh dev
```

### 4. 访问系统
- **前端**: http://localhost
- **后端API**: http://localhost:8000
- **管理后台**: http://localhost:8000/admin
- **默认管理员**: admin / admin123

## 🔧 详细部署步骤

### 步骤1: 环境准备

#### 安装Docker (Ubuntu/Debian)
```bash
# 更新包索引
sudo apt update

# 安装必要的包
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 将用户添加到docker组
sudo usermod -aG docker $USER
```

#### 安装Docker (CentOS/RHEL)
```bash
# 安装必要的包
sudo yum install -y yum-utils

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 步骤2: 配置环境变量

编辑 `.env` 文件，配置以下关键参数：

```bash
# 数据库配置
DB_PASSWORD=your_secure_password_here
DB_HOST=db
DB_PORT=5432
DB_NAME=course_management
DB_USER=postgres

# Redis配置
REDIS_PASSWORD=your_redis_password_here

# Django配置
SECRET_KEY=your-very-long-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# 安全配置
SECURE_SSL_REDIRECT=True  # 生产环境设为True
```

### 步骤3: 构建和启动服务

#### 开发环境部署
```bash
# 方法1: 使用部署脚本（推荐）
./deployment/docker/deploy.sh dev

# 方法2: 手动部署
docker-compose build
docker-compose up -d db redis
sleep 10
docker-compose run --rm backend python manage.py migrate
docker-compose run --rm backend python manage.py createsuperuser
docker-compose up -d
```

#### 生产环境部署
```bash
# 使用生产配置
./deployment/docker/deploy.sh prod

# 或手动部署
docker-compose --profile production up -d
```

## 📊 服务管理

### 查看服务状态
```bash
# 查看所有服务状态
./deployment/docker/deploy.sh status

# 或使用docker-compose
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
./deployment/docker/deploy.sh logs

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 停止服务
```bash
# 停止所有服务
./deployment/docker/deploy.sh stop

# 或使用docker-compose
docker-compose down
```

## 💾 数据管理

### 数据备份
```bash
# 使用部署脚本备份
./deployment/docker/deploy.sh backup

# 手动备份数据库
docker-compose exec -T db pg_dump -U postgres course_management > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份媒体文件
docker run --rm -v course-management-system_media_volume:/data -v $(pwd):/backup alpine tar czf /backup/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### 数据恢复
```bash
# 使用部署脚本恢复
./deployment/docker/deploy.sh restore backup_file.sql

# 手动恢复数据库
docker-compose exec -T db psql -U postgres -d course_management < backup_file.sql
```

## 🔍 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000

# 修改docker-compose.yml中的端口映射
ports:
  - "8080:80"  # 将80改为8080
```

#### 2. 数据库连接失败
```bash
# 检查数据库容器状态
docker-compose logs db

# 重启数据库服务
docker-compose restart db

# 检查环境变量配置
cat .env | grep DB_
```

#### 3. 前端无法访问后端API
```bash
# 检查网络连接
docker-compose exec frontend ping backend

# 检查nginx配置
docker-compose exec frontend cat /etc/nginx/nginx.conf

# 重启前端服务
docker-compose restart frontend
```

#### 4. 静态文件无法加载
```bash
# 重新收集静态文件
docker-compose exec backend python manage.py collectstatic --noinput

# 检查静态文件卷
docker volume inspect course-management-system_static_volume
```

### 日志分析

#### 查看详细错误日志
```bash
# Django应用日志
docker-compose exec backend tail -f /app/logs/django.log

# Nginx访问日志
docker-compose exec frontend tail -f /var/log/nginx/access.log

# Nginx错误日志
docker-compose exec frontend tail -f /var/log/nginx/error.log

# PostgreSQL日志
docker-compose logs db
```

## 🔒 安全配置

### 生产环境安全检查清单

- [ ] 修改默认密码
- [ ] 配置HTTPS证书
- [ ] 设置防火墙规则
- [ ] 启用安全头
- [ ] 配置备份策略
- [ ] 设置监控告警

### HTTPS配置

#### 使用Let's Encrypt证书
```bash
# 安装certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 修改nginx配置支持HTTPS
# 在nginx.conf中添加SSL配置
```

### 防火墙配置
```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 📈 性能优化

### 资源限制配置

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### 数据库优化

```sql
-- 在PostgreSQL中执行
-- 调整配置参数
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
```

## 🔄 更新和维护

### 应用更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建并部署
./deployment/docker/deploy.sh rebuild
```

### 系统维护
```bash
# 清理未使用的Docker资源
docker system prune -f

# 清理未使用的卷
docker volume prune -f

# 清理未使用的镜像
docker image prune -f
```

## 📞 技术支持

### 获取帮助
- 查看项目文档
- 检查GitHub Issues
- 联系开发团队

### 报告问题
请提供以下信息：
- 操作系统版本
- Docker版本
- 错误日志
- 复现步骤

---

**文档版本**: v1.0  
**最后更新**: 2024年8月14日  
**维护者**: 开发团队
