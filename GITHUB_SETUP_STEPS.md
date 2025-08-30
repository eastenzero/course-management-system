# GitHub仓库创建与配置详细指南

## 第一步：在GitHub创建仓库

### 1. 登录GitHub
- 打开浏览器，访问：https://github.com
- 使用你的账号密码登录

### 2. 创建新仓库
1. 点击右上角的 "+" 号
2. 选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `course-management-system`
   - **Description**: `校园课程管理系统 - 智能排课算法与现代化界面`
   - **设置为 Private**（推荐，保护你的代码）
   - **重要：不要勾选任何初始化选项**（README、.gitignore、license都不要勾选）
4. 点击 "Create repository"

### 3. 复制仓库URL
创建成功后，GitHub会显示一个页面，找到类似这样的URL：
```
https://github.com/你的用户名/course-management-system.git
```
复制这个URL，我们马上会用到。

## 第二步：连接本地仓库（我来执行）

你完成GitHub创建后，告诉我你的GitHub用户名，我会立即执行以下命令：

1. 添加远程仓库
2. 推送代码到GitHub
3. 验证连接成功

## 第三步：首次推送验证

推送时可能需要你的GitHub凭证：
- **用户名**：你的GitHub用户名
- **密码**：建议使用Personal Access Token（我会指导你创建）

## 如果需要Personal Access Token

如果推送时提示需要token：
1. 在GitHub上：Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token"
3. 设置权限：勾选 "repo" （完整仓库权限）
4. 生成后复制token（只显示一次，请保存好）
5. 推送时用token替代密码

---

## 完成后你会获得：
✅ GitHub上的完整项目仓库
✅ 本地与远程的同步连接
✅ 团队协作的基础
✅ 代码备份与版本管理