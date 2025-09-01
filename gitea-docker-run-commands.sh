# Gitea Docker Run 命令集合

# ==================== 针对你的Gitea服务器配置 ====================
# Gitea服务器: http://192.168.100.176:13000/
# SSH端口: 222
# 账号: easten
# 密码: ZhaYeFan05.07.14

# 配置Git远程仓库
git remote add gitea http://easten@192.168.100.176:13000/easten/course-management-system.git

# 或使用SSH (需要先配置SSH密钥)
git remote add gitea ssh://easten@192.168.100.176:222/easten/course-management-system.git

# ==================== 基础版本 (SQLite) ====================
# 简单启动，使用内置SQLite数据库
docker run -d \
  --name gitea \
  --restart always \
  -p 3000:3000 \
  -p 222:22 \
  -e USER_UID=1000 \
  -e USER_GID=1000 \
  -v ./gitea:/data \
  -v /etc/timezone:/etc/timezone:ro \
  -v /etc/localtime:/etc/localtime:ro \
  docker.gitea.com/gitea:1.24.5

# ==================== 自定义端口版本 ====================
# 避免端口冲突，使用8080和2222端口
docker run -d \
  --name gitea-custom \
  --restart always \
  -p 8080:3000 \
  -p 2222:22 \
  -e USER_UID=1000 \
  -e USER_GID=1000 \
  -e GITEA__server__DOMAIN=localhost \
  -e GITEA__server__ROOT_URL=http://localhost:8080/ \
  -v gitea_data:/data \
  -v /etc/timezone:/etc/timezone:ro \
  -v /etc/localtime:/etc/localtime:ro \
  docker.gitea.com/gitea:1.24.5

# ==================== 管理命令 ====================
# 查看日志
docker logs -f gitea

# 停止容器
docker stop gitea

# 删除容器 (保留数据)
docker rm gitea

# 更新到最新版本
docker pull docker.gitea.com/gitea:latest
docker stop gitea
docker rm gitea
# 然后重新运行上面的命令，镜像标签改为 :latest