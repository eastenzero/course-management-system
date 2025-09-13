# Gitea 双仓库快速配置脚本
Write-Host "配置双Git仓库同步 (easten@192.168.100.176:13000)" -ForegroundColor Green

# 检查当前是否在Git仓库中
if (-not (Test-Path ".git")) {
    Write-Host "错误: 当前目录不是Git仓库！" -ForegroundColor Red
    exit 1
}

# 显示当前远程配置
Write-Host "`n当前远程仓库配置:" -ForegroundColor Cyan
git remote -v

# 检查gitea远程是否已存在
$giteaExists = git remote | Select-String "gitea"
if ($giteaExists) {
    Write-Host "`n警告: Gitea远程仓库已存在，将更新配置..." -ForegroundColor Yellow
    git remote remove gitea
}

# 添加Gitea远程仓库
$giteaUrl = "http://easten@192.168.100.176:13000/easten/course-management-system.git"
Write-Host "`n添加Gitea远程仓库: $giteaUrl" -ForegroundColor Yellow
git remote add gitea $giteaUrl

# 配置origin同时推送到两个远程仓库
Write-Host "`n配置origin同时推送到GitHub和Gitea..." -ForegroundColor Yellow
$githubUrl = git remote get-url origin
git remote set-url --add --push origin $githubUrl
git remote set-url --add --push origin $giteaUrl

Write-Host "`n配置完成！" -ForegroundColor Green
Write-Host "`n新的远程仓库配置:" -ForegroundColor Cyan
git remote -v

Write-Host "`n使用说明:" -ForegroundColor White
Write-Host "  推送到所有远程: git push origin main" -ForegroundColor Gray
Write-Host "  仅推送到GitHub: git push origin main (需要移除Gitea push URL)" -ForegroundColor Gray  
Write-Host "  仅推送到Gitea:  git push gitea main" -ForegroundColor Gray
Write-Host "  SSH克隆地址: ssh://easten@192.168.100.176:222/easten/course-management-system.git" -ForegroundColor Cyan
Write-Host "  拉取 (从GitHub): git pull origin main" -ForegroundColor Gray

Write-Host "`n重要提示:" -ForegroundColor Yellow
Write-Host "  1. 请确保在Gitea中已创建 'course-management-system' 仓库" -ForegroundColor Yellow
Write-Host "  2. 访问地址: http://192.168.100.176:13000/" -ForegroundColor Yellow
Write-Host "  3. 使用账号: easten / 密码: ZhaYeFan05.07.14" -ForegroundColor Yellow
Write-Host "  4. 首次推送时需要输入Gitea账户凭据" -ForegroundColor Yellow

Write-Host "`n下一步操作:" -ForegroundColor Cyan
Write-Host "  1. 在Gitea中创建仓库" -ForegroundColor Gray
Write-Host "  2. 执行: git push origin main (推送到双远程)" -ForegroundColor Gray