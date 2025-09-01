# Gitea Docker 快速启动脚本
# 使用方法：PowerShell -ExecutionPolicy Bypass -File start-gitea.ps1

param(
    [string]$Type = "basic",  # basic, postgres, custom
    [switch]$Stop = $false
)

$configs = @{
    "basic" = "gitea-basic-docker-compose.yml"
    "postgres" = "gitea-postgres-docker-compose.yml" 
    "custom" = "gitea-custom-port-docker-compose.yml"
}

if (-not $configs.ContainsKey($Type)) {
    Write-Host "❌ 无效的类型。可用选项: basic, postgres, custom" -ForegroundColor Red
    exit 1
}

$configFile = $configs[$Type]

if (-not (Test-Path $configFile)) {
    Write-Host "❌ 配置文件不存在: $configFile" -ForegroundColor Red
    exit 1
}

if ($Stop) {
    Write-Host "🛑 停止Gitea服务..." -ForegroundColor Yellow
    docker-compose -f $configFile down
} else {
    Write-Host "🚀 启动Gitea服务 ($Type 模式)..." -ForegroundColor Green
    
    # 创建数据目录
    if (-not (Test-Path "gitea")) {
        New-Item -ItemType Directory -Name "gitea" -Force
        Write-Host "📁 已创建 gitea 数据目录" -ForegroundColor Cyan
    }
    
    # 启动服务
    docker-compose -f $configFile up -d
    
    # 显示访问信息
    Write-Host ""
    Write-Host "✅ Gitea 启动完成！" -ForegroundColor Green
    Write-Host ""
    
    switch ($Type) {
        "basic" { 
            Write-Host "🌐 Web访问: http://localhost:3000" -ForegroundColor Cyan
            Write-Host "🔑 SSH克隆: ssh://git@localhost:222/username/repo.git" -ForegroundColor Cyan
        }
        "postgres" { 
            Write-Host "🌐 Web访问: http://localhost:3000" -ForegroundColor Cyan
            Write-Host "🔑 SSH克隆: ssh://git@localhost:222/username/repo.git" -ForegroundColor Cyan
            Write-Host "🗄️  数据库: PostgreSQL (内置)" -ForegroundColor Cyan
        }
        "custom" { 
            Write-Host "🌐 Web访问: http://localhost:8080" -ForegroundColor Cyan
            Write-Host "🔑 SSH克隆: ssh://git@localhost:2222/username/repo.git" -ForegroundColor Cyan
        }
    }
    
    Write-Host ""
    Write-Host "📝 首次访问时需要完成安装向导" -ForegroundColor Yellow
    Write-Host "🔧 查看日志: docker-compose -f $configFile logs -f" -ForegroundColor Gray
    Write-Host "🛑 停止服务: .\start-gitea.ps1 -Type $Type -Stop" -ForegroundColor Gray
}