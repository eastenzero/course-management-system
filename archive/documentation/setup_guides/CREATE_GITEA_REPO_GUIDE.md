# 在Gitea中创建仓库指南

## 🎯 目标
在你的Gitea服务器中创建 `course-management-system` 仓库以支持全量备份

## 📋 详细步骤

### 1. 访问Gitea Web界面
- 打开浏览器
- 访问：http://192.168.100.176:13000/
- 确保能正常打开Gitea首页

### 2. 登录账户
- 点击右上角 "登录" 按钮
- 用户名：`easten`
- 密码：`ZhaYeFan05.07.14`
- 点击 "登录"

### 3. 创建新仓库
- 登录成功后，点击右上角的 "+" 号
- 选择 "新建仓库" (New Repository)
- 填写仓库信息：
  - **仓库名称**：`course-management-system`
  - **描述**（可选）：校园课程管理系统 - 支持智能排课和百万级数据处理
  - **可见性**：选择 "私有" (Private) 或 "公开" (Public)
  - **不要勾选**：初始化仓库、添加README、添加.gitignore、添加许可证

### 4. 确认创建
- 检查信息无误后，点击 "创建仓库" 按钮
- 系统会显示一个空的仓库页面

### 5. 验证仓库创建成功
- 你应该看到类似这样的URL：http://192.168.100.176:13000/easten/course-management-system
- 页面显示仓库为空，并提供推送指令

## 🚀 创建完成后测试推送

仓库创建成功后，运行以下命令测试推送：

```powershell
# 测试推送到Gitea
.\backup-to-gitea.ps1
```

或者单独测试Gitea推送：
```powershell
git push gitea main
```

## 📝 预期结果

创建成功后，你应该能看到：
- ✅ Gitea推送成功
- ✅ 所有748个文件完整备份到Gitea
- ✅ 双重备份保障（GitHub + Gitea）

## 🔧 故障排除

如果仍然遇到403错误：

1. **检查仓库名称**：确保是 `course-management-system`
2. **检查用户权限**：确认用户 `easten` 有创建仓库的权限
3. **重新生成Access Token**（如果需要）
4. **尝试SSH方式**（需要配置SSH密钥）

## 📞 需要帮助？

完成创建后，请告诉我结果，我会帮你进行最终的测试和验证！