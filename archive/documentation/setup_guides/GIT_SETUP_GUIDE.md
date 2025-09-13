# Git远程仓库配置说明

## 步骤1: 添加远程仓库
git remote add origin https://github.com/你的用户名/course-management-system.git

## 步骤2: 推送代码到远程仓库
git branch -M main
git push -u origin main

## 步骤3: 验证推送成功
git remote -v

## 常用命令
# 查看远程仓库
git remote -v

# 推送代码
git push origin main

# 拉取最新代码
git pull origin main

# 查看分支状态
git status

## 注意事项
1. 首次推送需要GitHub登录验证
2. 如果使用HTTPS，可能需要Personal Access Token
3. 建议使用SSH密钥进行验证（更安全）