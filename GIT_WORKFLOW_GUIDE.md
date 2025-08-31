# Git日常使用指南

## 基本工作流程

### 1. 开始工作前
```bash
# 拉取最新代码
git pull origin main

# 查看当前状态
git status
```

### 2. 开发过程中
```bash
# 查看修改的文件
git status

# 添加文件到暂存区
git add .                    # 添加所有修改
git add 文件名               # 添加特定文件

# 提交更改
git commit -m "描述你的修改内容"
```

### 3. 推送到远程
```bash
# 推送到远程仓库
git push origin main
```

## 常用命令

### 查看信息
```bash
git log --oneline           # 查看提交历史
git diff                    # 查看未暂存的修改
git diff --staged          # 查看已暂存的修改
git branch -a              # 查看所有分支
```

### 分支操作
```bash
git checkout -b feature/新功能    # 创建并切换到新分支
git checkout main                # 切换到主分支
git merge feature/新功能         # 合并分支
git branch -d feature/新功能     # 删除分支
```

### 撤销操作
```bash
git checkout -- 文件名          # 撤销未暂存的修改
git reset HEAD 文件名           # 取消暂存
git reset --hard HEAD~1        # 撤销最近一次提交
```

## 最佳实践

1. **频繁提交**: 小步快跑，经常提交代码
2. **清晰的提交信息**: 用简洁明了的中文描述修改内容
3. **使用分支**: 为新功能创建独立分支
4. **拉取后推送**: 推送前先拉取最新代码
5. **定期备份**: 定期推送到远程仓库

## 提交信息规范
```
feat: 新增功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建过程或辅助工具的变动
```

### 示例
```bash
git commit -m "feat: 添加学生课程选择功能"
git commit -m "fix: 修复登录验证错误"
git commit -m "docs: 更新安装说明文档"
```