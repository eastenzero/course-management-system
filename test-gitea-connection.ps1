# Gitea 连接测试脚本
# 使用方法：PowerShell -ExecutionPolicy Bypass -File test-gitea-connection.ps1

Write-Host "🔍 测试Gitea服务器连接" -ForegroundColor Green
Write-Host "=" * 40 -ForegroundColor Gray

$giteaHost = "192.168.100.176"
$giteaPort = 13000
$sshPort = 222

# 测试Web端口连接
Write-Host "`n📡 测试Web端口连接 (${giteaHost}:${giteaPort})..." -ForegroundColor Cyan
try {
    $webTest = Test-NetConnection -ComputerName $giteaHost -Port $giteaPort -WarningAction SilentlyContinue
    if ($webTest.TcpTestSucceeded) {
        Write-Host "✅ Web端口连接成功！" -ForegroundColor Green
        
        # 尝试访问Gitea Web界面
        try {
            $response = Invoke-WebRequest -Uri "http://${giteaHost}:${giteaPort}" -Method Head -TimeoutSec 10 -ErrorAction Stop
            Write-Host "✅ Gitea Web服务响应正常！" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Web端口开放但Gitea服务可能未运行" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Web端口连接失败" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Web端口测试出错: $_" -ForegroundColor Red
}

# 测试SSH端口连接
Write-Host "`n🔑 测试SSH端口连接 (${giteaHost}:${sshPort})..." -ForegroundColor Cyan
try {
    $sshTest = Test-NetConnection -ComputerName $giteaHost -Port $sshPort -WarningAction SilentlyContinue
    if ($sshTest.TcpTestSucceeded) {
        Write-Host "✅ SSH端口连接成功！" -ForegroundColor Green
    } else {
        Write-Host "❌ SSH端口连接失败" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ SSH端口测试出错: $_" -ForegroundColor Red
}

# 检查当前Git配置
Write-Host "`n📋 当前Git远程配置:" -ForegroundColor Cyan
if (Test-Path ".git") {
    git remote -v
    
    # 检查gitea远程是否已配置
    $giteaRemote = git remote | Select-String "gitea"
    if ($giteaRemote) {
        Write-Host "`n🔍 测试Gitea远程仓库连接..." -ForegroundColor Cyan
        try {
            $giteaUrl = git remote get-url gitea
            Write-Host "Gitea远程URL: $giteaUrl" -ForegroundColor Gray
            
            # 测试git连接
            git ls-remote gitea 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Gitea Git仓库连接成功！" -ForegroundColor Green
            } else {
                Write-Host "❌ Gitea Git仓库连接失败" -ForegroundColor Red
                Write-Host "💡 可能需要在Gitea中创建仓库或检查认证信息" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Gitea远程测试出错: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "ℹ️  未配置Gitea远程仓库" -ForegroundColor Yellow
        Write-Host "运行 .\setup-easten-gitea.ps1 进行配置" -ForegroundColor Gray
    }
} else {
    Write-Host "ℹ️  当前目录不是Git仓库" -ForegroundColor Yellow
}

Write-Host "`n📝 连接信息总结:" -ForegroundColor White
Write-Host "  🌐 Gitea Web: http://${giteaHost}:${giteaPort}/" -ForegroundColor Gray
Write-Host "  👤 用户名: easten" -ForegroundColor Gray
Write-Host "  🔑 SSH: ssh://easten@${giteaHost}:${sshPort}/easten/repo.git" -ForegroundColor Gray
Write-Host "  📁 HTTP: http://easten@${giteaHost}:${giteaPort}/easten/repo.git" -ForegroundColor Gray