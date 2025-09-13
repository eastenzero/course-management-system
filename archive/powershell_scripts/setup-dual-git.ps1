# Git 多远程仓库配置脚本
# 使用方法：PowerShell -ExecutionPolicy Bypass -File setup-dual-git.ps1

param(
    [string]$GiteaUrl = "http://192.168.100.176:13000",  # Gitea URL
    [string]$GiteaUser = "easten",                       # Gitea 用户名
    [string]$RepoName = "course-management-system"      # 仓库名称
)

Write-Host "🔧 配置Git多远程仓库同步..." -ForegroundColor Green

# 检查当前是否在Git仓库中
if (-not (Test-Path ".git")) {
    Write-Host "❌ 当前目录不是Git仓库！" -ForegroundColor Red
    exit 1
}

# 显示当前远程配置
Write-Host "`n📋 当前远程仓库配置:" -ForegroundColor Cyan
git remote -v

# 添加Gitea远程仓库
$giteaRemoteUrl = "http://$GiteaUser@192.168.100.176:13000/$GiteaUser/$RepoName.git"
Write-Host "`n➕ 添加Gitea远程仓库..." -ForegroundColor Yellow
git remote add gitea $giteaRemoteUrl

# 方案A：为origin添加多个push URL
Write-Host "`n🔄 配置origin同时推送到两个远程仓库..." -ForegroundColor Yellow
$githubUrl = git remote get-url origin
git remote set-url --add --push origin $githubUrl
git remote set-url --add --push origin $giteaRemoteUrl

Write-Host "`n✅ 配置完成！" -ForegroundColor Green
Write-Host "`n📋 新的远程仓库配置:" -ForegroundColor Cyan
git remote -v

Write-Host "`n📝 使用说明:" -ForegroundColor White
Write-Host "  🚀 推送到所有远程: git push origin main" -ForegroundColor Gray
Write-Host "  🎯 仅推送到GitHub: git push origin main --push-option=-all" -ForegroundColor Gray  
Write-Host "  🏠 仅推送到Gitea:  git push gitea main" -ForegroundColor Gray
Write-Host "  🔑 SSH克隆: ssh://easten@192.168.100.176:222/easten/course-management-system.git" -ForegroundColor Cyan
Write-Host "  📥 拉取 (从GitHub): git pull origin main" -ForegroundColor Gray

Write-Host "`n⚠️  重要提示:" -ForegroundColor Yellow
Write-Host "  1. 首先确保Gitea服务已启动并创建了仓库" -ForegroundColor Yellow
Write-Host "  2. 在Gitea中创建同名仓库: $RepoName (地址: $GiteaUrl)" -ForegroundColor Yellow
Write-Host "  3. 首次推送时可能需要输入Gitea账户凭据" -ForegroundColor Yellow