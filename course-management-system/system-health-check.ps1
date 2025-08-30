#!/usr/bin/env pwsh
<#
.SYNOPSIS
    校园课程管理系统 - 系统健康检查和启动脚本
.DESCRIPTION
    检测前端、后端、数据库的连接性，并提供系统启动功能
.AUTHOR
    Course Management System Team
#>

# 设置错误处理
$ErrorActionPreference = "Continue"

# 颜色定义
$Colors = @{
    Green = "Green"
    Red = "Red"
    Yellow = "Yellow"
    Blue = "Cyan"
    White = "White"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Test-Port {
    param(
        [string]$Host = "localhost",
        [int]$Port,
        [int]$Timeout = 3
    )
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $asyncResult = $tcpClient.BeginConnect($Host, $Port, $null, $null)
        $wait = $asyncResult.AsyncWaitHandle.WaitOne($Timeout * 1000, $false)
        
        if ($wait) {
            try {
                $tcpClient.EndConnect($asyncResult)
                $tcpClient.Close()
                return $true
            }
            catch {
                return $false
            }
        }
        else {
            $tcpClient.Close()
            return $false
        }
    }
    catch {
        return $false
    }
}

function Test-HttpEndpoint {
    param(
        [string]$Url,
        [int]$Timeout = 10
    )
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec $Timeout -UseBasicParsing -ErrorAction Stop
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function Check-Prerequisites {
    Write-ColorOutput "🔍 检查系统先决条件..." "Blue"
    $allGood = $true
    
    # 检查 Docker
    if (Test-Command "docker") {
        $dockerVersion = docker --version 2>$null
        Write-ColorOutput "  ✅ Docker: $dockerVersion" "Green"
        
        # 检查 Docker Compose
        if (Test-Command "docker-compose") {
            $composeVersion = docker-compose --version 2>$null
            Write-ColorOutput "  ✅ Docker Compose: $composeVersion" "Green"
        }
        else {
            Write-ColorOutput "  ❌ Docker Compose 未安装" "Red"
            $allGood = $false
        }
    }
    else {
        Write-ColorOutput "  ❌ Docker 未安装" "Red"
        $allGood = $false
    }
    
    # 检查 Node.js (用于前端开发)
    if (Test-Command "node") {
        $nodeVersion = node --version 2>$null
        Write-ColorOutput "  ✅ Node.js: $nodeVersion" "Green"
    }
    else {
        Write-ColorOutput "  ⚠️  Node.js 未安装 (仅影响开发模式)" "Yellow"
    }
    
    # 检查 Python (用于后端开发)
    if (Test-Command "python") {
        $pythonVersion = python --version 2>$null
        Write-ColorOutput "  ✅ Python: $pythonVersion" "Green"
    }
    else {
        Write-ColorOutput "  ⚠️  Python 未安装 (仅影响开发模式)" "Yellow"
    }
    
    return $allGood
}

function Check-DockerServices {
    Write-ColorOutput "🐳 检查 Docker 服务状态..." "Blue"
    
    try {
        $services = docker-compose ps --format json 2>$null | ConvertFrom-Json
        if ($services) {
            foreach ($service in $services) {
                $status = if ($service.State -eq "running") { "✅" } else { "❌" }
                $color = if ($service.State -eq "running") { "Green" } else { "Red" }
                Write-ColorOutput "  $status $($service.Service): $($service.State)" $color
            }
            return $true
        }
        else {
            Write-ColorOutput "  ❌ 没有运行的服务" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "  ❌ 无法获取服务状态" "Red"
        return $false
    }
}

function Check-DatabaseConnection {
    Write-ColorOutput "🗄️  检查数据库连接..." "Blue"
    
    # 检查 PostgreSQL 端口
    if (Test-Port -Port 5432) {
        Write-ColorOutput "  ✅ PostgreSQL 端口 5432 可访问" "Green"
        
        # 尝试通过 Docker 检查数据库连接
        try {
            $result = docker-compose exec -T db pg_isready -U postgres 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "  ✅ PostgreSQL 数据库连接正常" "Green"
                return $true
            }
            else {
                Write-ColorOutput "  ❌ PostgreSQL 数据库连接失败" "Red"
                return $false
            }
        }
        catch {
            Write-ColorOutput "  ⚠️  无法通过 Docker 检查数据库状态" "Yellow"
            return $false
        }
    }
    else {
        Write-ColorOutput "  ❌ PostgreSQL 端口 5432 不可访问" "Red"
        return $false
    }
}

function Check-RedisConnection {
    Write-ColorOutput "🔴 检查 Redis 连接..." "Blue"
    
    # 检查 Redis 端口
    if (Test-Port -Port 6379) {
        Write-ColorOutput "  ✅ Redis 端口 6379 可访问" "Green"
        
        # 尝试通过 Docker 检查 Redis 连接
        try {
            $result = docker-compose exec -T redis redis-cli ping 2>$null
            if ($result -match "PONG") {
                Write-ColorOutput "  ✅ Redis 连接正常" "Green"
                return $true
            }
            else {
                Write-ColorOutput "  ❌ Redis 连接失败" "Red"
                return $false
            }
        }
        catch {
            Write-ColorOutput "  ⚠️  无法通过 Docker 检查 Redis 状态" "Yellow"
            return $false
        }
    }
    else {
        Write-ColorOutput "  ❌ Redis 端口 6379 不可访问" "Red"
        return $false
    }
}

function Check-BackendHealth {
    Write-ColorOutput "🔧 检查后端服务..." "Blue"
    
    # 检查后端端口
    if (Test-Port -Port 8000) {
        Write-ColorOutput "  ✅ 后端端口 8000 可访问" "Green"
        
        # 检查健康检查端点
        if (Test-HttpEndpoint -Url "http://localhost:8000/api/health/") {
            Write-ColorOutput "  ✅ 后端健康检查通过" "Green"
            return $true
        }
        else {
            Write-ColorOutput "  ❌ 后端健康检查失败" "Red"
            return $false
        }
    }
    else {
        Write-ColorOutput "  ❌ 后端端口 8000 不可访问" "Red"
        return $false
    }
}

function Check-FrontendHealth {
    Write-ColorOutput "🎨 检查前端服务..." "Blue"
    
    # 检查前端端口 (Docker 模式)
    if (Test-Port -Port 8081) {
        Write-ColorOutput "  ✅ 前端端口 8081 可访问" "Green"
        
        # 检查前端页面
        if (Test-HttpEndpoint -Url "http://localhost:8081") {
            Write-ColorOutput "  ✅ 前端页面可访问" "Green"
            return $true
        }
        else {
            Write-ColorOutput "  ❌ 前端页面不可访问" "Red"
            return $false
        }
    }
    # 检查开发模式端口
    elseif (Test-Port -Port 3000) {
        Write-ColorOutput "  ✅ 前端开发端口 3000 可访问" "Green"
        
        if (Test-HttpEndpoint -Url "http://localhost:3000") {
            Write-ColorOutput "  ✅ 前端开发页面可访问" "Green"
            return $true
        }
        else {
            Write-ColorOutput "  ❌ 前端开发页面不可访问" "Red"
            return $false
        }
    }
    else {
        Write-ColorOutput "  ❌ 前端服务不可访问 (端口 8081 或 3000)" "Red"
        return $false
    }
}

function Start-System {
    param([string]$Mode = "docker")
    
    Write-ColorOutput "🚀 启动系统 ($Mode 模式)..." "Blue"
    
    if ($Mode -eq "docker") {
        Write-ColorOutput "📦 启动 Docker 服务..." "Yellow"
        docker-compose up -d
        
        Write-ColorOutput "⏳ 等待服务启动..." "Yellow"
        Start-Sleep -Seconds 15
        
        Write-ColorOutput "🗄️  运行数据库迁移..." "Yellow"
        docker-compose exec -T backend python manage.py migrate
        
        Write-ColorOutput "👤 创建测试用户..." "Yellow"
        $createUserScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123', user_type='admin')
    print('✅ 管理员账号已创建: admin/admin123')
if not User.objects.filter(username='teacher1').exists():
    User.objects.create_user('teacher1', 'teacher1@example.com', 'teacher123', user_type='teacher', first_name='张', last_name='老师')
    print('✅ 教师账号已创建: teacher1/teacher123')
if not User.objects.filter(username='student1').exists():
    User.objects.create_user('student1', 'student1@example.com', 'student123', user_type='student', first_name='李', last_name='同学')
    print('✅ 学生账号已创建: student1/student123')
"@
        
        $createUserScript | docker-compose exec -T backend python manage.py shell
    }
    else {
        Write-ColorOutput "⚠️  开发模式启动需要手动操作" "Yellow"
        Write-ColorOutput "  1. 启动后端: cd backend && python manage.py runserver" "White"
        Write-ColorOutput "  2. 启动前端: cd frontend && npm run dev" "White"
    }
}

function Show-SystemInfo {
    Write-ColorOutput "📋 系统访问信息:" "Blue"
    Write-ColorOutput "  🌐 前端应用: http://localhost:8081" "Green"
    Write-ColorOutput "  🔧 后端API: http://localhost:8000" "Green"
    Write-ColorOutput "  📚 API文档: http://localhost:8000/api/docs/" "Green"
    Write-ColorOutput "  👨‍💼 管理后台: http://localhost:8000/admin" "Green"
    Write-ColorOutput "" "White"
    Write-ColorOutput "👤 测试账号:" "Blue"
    Write-ColorOutput "  管理员: admin / admin123" "Green"
    Write-ColorOutput "  教师: teacher1 / teacher123" "Green"
    Write-ColorOutput "  学生: student1 / student123" "Green"
    Write-ColorOutput "" "White"
    Write-ColorOutput "🔧 常用命令:" "Blue"
    Write-ColorOutput "  查看服务状态: docker-compose ps" "White"
    Write-ColorOutput "  查看日志: docker-compose logs -f" "White"
    Write-ColorOutput "  停止服务: docker-compose down" "White"
    Write-ColorOutput "  重启服务: docker-compose restart" "White"
}

function Main {
    param(
        [string]$Action = "check",
        [string]$Mode = "docker"
    )
    
    Write-ColorOutput "=" * 60 "Blue"
    Write-ColorOutput "🏫 校园课程管理系统 - 系统健康检查" "Blue"
    Write-ColorOutput "=" * 60 "Blue"
    
    # 检查先决条件
    if (-not (Check-Prerequisites)) {
        Write-ColorOutput "❌ 先决条件检查失败，请安装必要的软件" "Red"
        return 1
    }
    
    if ($Action -eq "start") {
        Start-System -Mode $Mode
        Start-Sleep -Seconds 5
    }
    
    # 执行健康检查
    Write-ColorOutput "`n🔍 开始系统健康检查..." "Blue"
    
    $checks = @(
        @{ Name = "Docker服务"; Function = { Check-DockerServices } },
        @{ Name = "数据库连接"; Function = { Check-DatabaseConnection } },
        @{ Name = "Redis连接"; Function = { Check-RedisConnection } },
        @{ Name = "后端服务"; Function = { Check-BackendHealth } },
        @{ Name = "前端服务"; Function = { Check-FrontendHealth } }
    )
    
    $results = @()
    foreach ($check in $checks) {
        Write-ColorOutput "" "White"
        try {
            $result = & $check.Function
            $results += @{ Name = $check.Name; Result = $result }
        }
        catch {
            Write-ColorOutput "  ❌ 检查 $($check.Name) 时出错: $($_.Exception.Message)" "Red"
            $results += @{ Name = $check.Name; Result = $false }
        }
    }
    
    # 显示总结
    Write-ColorOutput "`n" + "=" * 60 "Blue"
    Write-ColorOutput "📊 健康检查结果总结" "Blue"
    Write-ColorOutput "=" * 60 "Blue"
    
    $passed = 0
    $total = $results.Count
    
    foreach ($result in $results) {
        $status = if ($result.Result) { "✅ 正常" } else { "❌ 异常" }
        $color = if ($result.Result) { "Green" } else { "Red" }
        Write-ColorOutput ("{0,-15} {1}" -f $result.Name, $status) $color
        if ($result.Result) { $passed++ }
    }
    
    Write-ColorOutput "`n总计: $passed/$total 项检查通过" "White"
    
    if ($passed -eq $total) {
        Write-ColorOutput "`n🎉 所有系统组件运行正常！" "Green"
        Show-SystemInfo
        return 0
    }
    else {
        Write-ColorOutput "`n⚠️  有 $($total - $passed) 项检查失败，请检查相关服务" "Yellow"
        if ($Action -ne "start") {
            Write-ColorOutput "`n💡 尝试运行: .\system-health-check.ps1 -Action start" "Blue"
        }
        return 1
    }
}

# 参数处理
param(
    [Parameter(Position=0)]
    [ValidateSet("check", "start")]
    [string]$Action = "check",
    
    [Parameter(Position=1)]
    [ValidateSet("docker", "dev")]
    [string]$Mode = "docker"
)

# 执行主函数
exit (Main -Action $Action -Mode $Mode)
