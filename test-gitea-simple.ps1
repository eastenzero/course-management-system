# 最简化的Gitea连接测试
Write-Host "🔍 测试Gitea服务器连接" -ForegroundColor Green

# 连接信息
$host_ip = "192.168.100.176"
$web_port = 13000
$ssh_port = 222

Write-Host ""
Write-Host "📡 测试Web端口连接..." -ForegroundColor Cyan
$web_result = Test-NetConnection -ComputerName $host_ip -Port $web_port -WarningAction SilentlyContinue
if ($web_result.TcpTestSucceeded) {
    Write-Host "✅ Web端口 $web_port 连接成功！" -ForegroundColor Green
} else {
    Write-Host "❌ Web端口 $web_port 连接失败" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔑 测试SSH端口连接..." -ForegroundColor Cyan
$ssh_result = Test-NetConnection -ComputerName $host_ip -Port $ssh_port -WarningAction SilentlyContinue
if ($ssh_result.TcpTestSucceeded) {
    Write-Host "✅ SSH端口 $ssh_port 连接成功！" -ForegroundColor Green
} else {
    Write-Host "❌ SSH端口 $ssh_port 连接失败" -ForegroundColor Red
}

Write-Host ""
Write-Host "📋 Git远程配置:" -ForegroundColor Cyan
if (Test-Path ".git") {
    git remote -v
} else {
    Write-Host "ℹ️  当前目录不是Git仓库" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📝 Gitea服务器信息:" -ForegroundColor White
Write-Host "  🌐 Web地址: http://$host_ip`:$web_port/" -ForegroundColor Gray
Write-Host "  👤 用户名: easten" -ForegroundColor Gray
Write-Host "  🔐 密码: ZhaYeFan05.07.14" -ForegroundColor Gray
Write-Host "  🔑 SSH地址: ssh://easten@$host_ip`:$ssh_port/easten/repo.git" -ForegroundColor Gray
Write-Host "  📁 HTTP地址: http://easten@$host_ip`:$web_port/easten/repo.git" -ForegroundColor Gray