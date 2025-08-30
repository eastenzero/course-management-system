# 🚀 Docker 快速启动指南

## 📋 前置要求

确保您的系统已安装：
- Docker 20.10+
- Docker Compose 2.0+
- Git

## ⚡ 5分钟快速部署

### 1. 克隆项目
```bash
git clone <your-repository-url>
cd course-management-system
```

### 2. 配置环境
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑关键配置（可选，使用默认值也可以）
nano .env
```

### 3. 一键启动
```bash
# 开发环境（推荐新手）
./deployment/docker/deploy.sh dev

# 或者手动启动
docker-compose up -d
```

### 4. 访问系统
- 🌐 **前端**: http://localhost
- 🔧 **后端API**: http://localhost:8000
- 👨‍💼 **管理后台**: http://localhost:8000/admin
- 🔑 **默认管理员**: admin / admin123

## 🛠️ 常用命令

### 服务管理
```bash
# 查看服务状态
./deployment/docker/deploy.sh status

# 查看日志
./deployment/docker/deploy.sh logs

# 停止服务
./deployment/docker/deploy.sh stop

# 重新构建
./deployment/docker/deploy.sh rebuild
```

### 数据管理
```bash
# 备份数据
./deployment/docker/deploy.sh backup

# 恢复数据
./deployment/docker/deploy.sh restore backup_file.sql
```

## 🔧 故障排除

### 端口冲突
如果80端口被占用，修改 `docker-compose.yml`：
```yaml
frontend:
  ports:
    - "8080:80"  # 改为8080端口
```

### 权限问题
```bash
# 给脚本执行权限
chmod +x deployment/docker/deploy.sh

# 如果Docker需要sudo
sudo usermod -aG docker $USER
# 然后重新登录
```

### 数据库连接失败
```bash
# 重启数据库
docker-compose restart db

# 查看数据库日志
docker-compose logs db
```

## 📱 移动端测试

在同一网络下的移动设备访问：
```
http://你的电脑IP地址
```

查看电脑IP：
```bash
# Linux/Mac
ip addr show | grep inet

# Windows
ipconfig
```

## 🎯 下一步

1. **修改默认密码** - 进入管理后台修改admin密码
2. **添加测试数据** - 创建一些课程和用户进行测试
3. **配置邮件** - 在.env中配置邮件服务器
4. **部署到生产** - 使用 `docker-compose.prod.yml`

## 📞 获取帮助

- 📖 查看完整文档：`Docker部署技术文档.md`
- 🐛 遇到问题：检查日志文件
- 💬 技术支持：联系开发团队

---
**提示**: 首次启动可能需要几分钟下载镜像，请耐心等待。
