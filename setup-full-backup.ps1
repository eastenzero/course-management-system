# 简化的全量备份配置脚本
Write-Host "设置Gitea全量备份配置" -ForegroundColor Green

# 检查Git仓库
if (-not (Test-Path ".git")) {
    Write-Host "错误: 当前目录不是Git仓库！" -ForegroundColor Red
    exit 1
}

# 测试Gitea连接
Write-Host "`n测试Gitea连接..." -ForegroundColor Cyan
$giteaTest = Test-NetConnection -ComputerName 192.168.100.176 -Port 13000 -WarningAction SilentlyContinue
if ($giteaTest.TcpTestSucceeded) {
    Write-Host "✅ Gitea连接成功！" -ForegroundColor Green
} else {
    Write-Host "❌ Gitea连接失败" -ForegroundColor Red
    exit 1
}

# 检查.gitignore配置
Write-Host "`n检查.gitignore配置..." -ForegroundColor Cyan
$gitignorePath = ".gitignore"
if (Test-Path $gitignorePath) {
    $content = Get-Content $gitignorePath -Raw
    
    # 检查是否已有全量备份配置
    if (-not $content.Contains("# ===== 全量备份配置 =====")) {
        Write-Host "更新.gitignore以支持全量备份..." -ForegroundColor Yellow
        
        $backupConfig = @"

# ===== 全量备份配置 =====
# 排除敏感信息
.env
*.key
*.pem
secrets/
credentials/

# 排除临时文件
*.tmp
*.temp
*.cache
.DS_Store
Thumbs.db

# 确保重要文件被包含（已在现有配置中处理）
# 配置文件: *.yml, *.json, *.ini, requirements.txt
# 脚本工具: *.ps1, *.sh, *.bat  
# 文档资料: *.md, README*, LICENSE*
# Docker配置: Dockerfile, docker-compose*.yml

"@
        Add-Content -Path $gitignorePath -Value $backupConfig
        Write-Host "✅ 已更新.gitignore配置" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ .gitignore已包含全量备份配置" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ 未找到.gitignore文件" -ForegroundColor Red
}

# 显示当前状态
Write-Host "`n当前Git状态:" -ForegroundColor Cyan
git remote -v
Write-Host ""
git status --short

Write-Host "`n📊 全量备份覆盖范围:" -ForegroundColor White
Write-Host "✅ 项目源代码 (所有.py, .js, .css, .html文件)" -ForegroundColor Green
Write-Host "✅ 配置文件 (.yml, .json, .ini, requirements.txt)" -ForegroundColor Green  
Write-Host "✅ 脚本工具 (.ps1, .sh, .bat)" -ForegroundColor Green
Write-Host "✅ 文档资料 (.md, README*, LICENSE*)" -ForegroundColor Green
Write-Host "✅ Docker配置 (Dockerfile, docker-compose*.yml)" -ForegroundColor Green
Write-Host "❌ 大数据文件 (*.json, *.sql, *.csv 数据输出)" -ForegroundColor Red
Write-Host "❌ 敏感信息 (.env, *.key, *.pem)" -ForegroundColor Red
Write-Host "❌ 临时文件 (*.tmp, .cache, node_modules/)" -ForegroundColor Red

Write-Host "`n下一步操作:" -ForegroundColor Cyan
Write-Host "1. 在Gitea中创建仓库 'course-management-system'" -ForegroundColor Gray
Write-Host "   访问: http://192.168.100.176:13000/" -ForegroundColor Gray
Write-Host "   用户: easten / 密码: ZhaYeFan05.07.14" -ForegroundColor Gray
Write-Host "2. 执行全量备份: .\auto-backup-to-gitea.ps1" -ForegroundColor Gray

Write-Host "`n✅ 全量备份配置完成！" -ForegroundColor Green