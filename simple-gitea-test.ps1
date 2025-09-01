# 简化的Gitea连接测试脚本
Write-Host "🔍 测试Gitea服务器连接" -ForegroundColor Green

$giteaHost = "192.168.100.176"
$giteaPort = 13000
$sshPort = 222

# 测试Web端口
Write-Host "`n📡 测试Web端口连接 ($giteaHost:$giteaPort)..." -ForegroundColor Cyan
$webTest = Test-NetConnection -ComputerName $giteaHost -Port $giteaPort -WarningAction SilentlyContinue
if ($webTest.TcpTestSucceeded) {
    Write-Host "✅ Web端口连接成功！" -ForegroundColor Green
} else {
    Write-Host "❌ Web端口连接失败" -ForegroundColor Red
}

# 测试SSH端口
Write-Host "`n🔑 测试SSH端口连接 ($giteaHost:$sshPort)..." -ForegroundColor Cyan
$sshTest = Test-NetConnection -ComputerName $giteaHost -Port $sshPort -WarningAction SilentlyContinue
if ($sshTest.TcpTestSucceeded) {
    Write-Host "✅ SSH端口连接成功！" -ForegroundColor Green
} else {
    Write-Host "❌ SSH端口连接失败" -ForegroundColor Red
}

# 显示当前Git配置
Write-Host "`n📋 当前Git远程配置:" -ForegroundColor Cyan
if (Test-Path ".git") {
    git remote -v
} else {
    Write-Host "ℹ️  当前目录不是Git仓库" -ForegroundColor Yellow
}

Write-Host "`n📝 Gitea连接信息:" -ForegroundColor White
Write-Host "  🌐 Web访问: http://$giteaHost:$giteaPort/" -ForegroundColor Gray
Write-Host "  👤 用户名: easten" -ForegroundColor Gray
Write-Host "  🔐 密码: ZhaYeFan05.07.14" -ForegroundColor Gray
Write-Host "  🔑 SSH: ssh://easten@$giteaHost:$sshPort/easten/repo.git" -ForegroundColor Gray
Write-Host "  📁 HTTP: http://easten@$giteaHost:$giteaPort/easten/repo.git" -ForegroundColor Gray