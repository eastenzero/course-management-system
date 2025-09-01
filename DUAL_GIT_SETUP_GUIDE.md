# Git双仓库同步设置指南

## 🎯 目标
同时维护GitHub和本地Gitea两个Git仓库，实现代码的双重备份和管理。

## 📋 设置步骤

### 1. 启动Gitea服务
您的Gitea服务器已经配置在:
- **Web地址**: http://192.168.100.176:13000/
- **SSH端口**: 222
- **账号**: easten
- **密码**: ZhaYeFan05.07.14

### 2. 在Gitea中创建仓库
1. 访问 http://192.168.100.176:13000/
2. 使用账号: easten 密码: ZhaYeFan05.07.14 登录
3. 创建新仓库：`course-management-system`

### 3. 配置双远程仓库
```powershell
# 自动配置双远程
.\setup-dual-git.ps1

# 或手动配置
git remote add gitea http://easten@192.168.100.176:13000/easten/course-management-system.git
```

### 4. 设置Git别名（可选）
```powershell
.\git-sync-aliases.ps1
```

## 🚀 日常使用方法

### 方法一：使用管理脚本（推荐）
```powershell
# 查看状态
.\git-dual-sync.ps1 -Action status

# 推送到双远程
.\git-dual-sync.ps1 -Action push -Message "feat: 新功能"

# 完整同步（拉取+推送）
.\git-dual-sync.ps1 -Action sync -Message "update: 更新代码"
```

### 方法二：使用Git别名
```powershell
# 推送到所有远程
git sync-all main

# 仅推送到GitHub
git push-github main

# 仅推送到Gitea
git push-gitea main
```

### 方法三：原生Git命令
```powershell
# 推送到GitHub
git push origin main

# 推送到Gitea
git push gitea main

# 推送到所有远程（如果配置了多个push URL）
git push origin main  # 会同时推送到GitHub和Gitea
```

## 🔧 高级配置

### SSH密钥配置（推荐）
```powershell
# 为Gitea生成专用SSH密钥
ssh-keygen -t rsa -b 4096 -C "your-email@example.com" -f ~/.ssh/id_rsa_gitea

# 在Gitea中添加公钥
# 然后修改远程URL为SSH格式
git remote set-url gitea ssh://easten@192.168.100.176:222/easten/course-management-system.git
```

### 自动同步钩子
可以设置Git钩子，在每次提交后自动推送到双远程：
```bash
# .git/hooks/post-commit
#!/bin/sh
git push origin main
git push gitea main
```

## 📝 工作流程建议

### 日常开发流程
1. `git pull origin main` - 从GitHub拉取最新代码
2. 进行开发和修改
3. `git add .` - 添加更改
4. `git commit -m "描述"` - 提交更改
5. `.\git-dual-sync.ps1 -Action push -Message "描述"` - 推送到双远程

### 备份策略
- **主仓库**：GitHub（公开，协作）
- **备份仓库**：本地Gitea（私有，安全）
- **拉取策略**：始终从GitHub拉取（保持主线同步）
- **推送策略**：同时推送到两个仓库（双重备份）

## ⚠️ 注意事项

1. **Gitea服务状态**：确保Gitea容器正在运行
2. **网络连接**：Gitea推送失败时检查本地网络
3. **认证配置**：首次推送可能需要输入凭据
4. **冲突处理**：如果两个仓库出现分歧，以GitHub为准
5. **大文件管理**：确保.gitignore正确配置，避免推送大文件

## 🆘 故障排除

### Gitea推送失败
```powershell
# 检查Gitea服务状态
docker-compose -f gitea-postgres-docker-compose.yml ps

# 查看Gitea日志
docker-compose -f gitea-postgres-docker-compose.yml logs gitea

# 重启Gitea服务
docker-compose -f gitea-postgres-docker-compose.yml restart
```

### 远程URL错误
```powershell
# 查看当前远程配置
git remote -v

# 修正Gitea远程URL
git remote set-url gitea http://easten@192.168.100.176:13000/easten/course-management-system.git
```

## 🎉 完成！
现在你的代码将同时备份到GitHub和本地Gitea，享受双重安全保障！