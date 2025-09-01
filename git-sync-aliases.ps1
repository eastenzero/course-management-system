# Git 同步别名配置脚本
# 为Git添加便捷的同步命令别名

Write-Host "🔧 配置Git同步别名..." -ForegroundColor Green

# 添加Git别名
Write-Host "➕ 添加Git别名..." -ForegroundColor Yellow

# 同步到所有远程仓库
git config alias.sync-all "!f() { git push origin \$1 && git push gitea \$1; }; f"

# 拉取并推送到所有远程
git config alias.sync-push "!f() { git pull origin \$1 && git push origin \$1 && git push gitea \$1; }; f"

# 快速状态检查
git config alias.remote-status "!git remote -v"

# 推送到GitHub
git config alias.push-github "!f() { git push origin \$1; }; f"

# 推送到Gitea  
git config alias.push-gitea "!f() { git push gitea \$1; }; f"

Write-Host "✅ 别名配置完成！" -ForegroundColor Green

Write-Host "`n📝 可用的Git别名:" -ForegroundColor Cyan
Write-Host "  git sync-all main        - 推送到所有远程仓库" -ForegroundColor Gray
Write-Host "  git sync-push main       - 拉取后推送到所有远程" -ForegroundColor Gray
Write-Host "  git push-github main     - 仅推送到GitHub" -ForegroundColor Gray
Write-Host "  git push-gitea main      - 仅推送到Gitea" -ForegroundColor Gray
Write-Host "  git remote-status        - 查看远程仓库状态" -ForegroundColor Gray

Write-Host "`n🎯 日常使用示例:" -ForegroundColor White
Write-Host "  1. 修改代码后: git add . && git commit -m 'update'" -ForegroundColor Gray
Write-Host "  2. 同步到所有: git sync-all main" -ForegroundColor Gray