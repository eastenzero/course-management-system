# UI重新设计项目状态检查脚本

Write-Host "🔍 检查UI重新设计项目状态..." -ForegroundColor Cyan
Write-Host ""

# 检查Docker容器状态
Write-Host "📦 Docker容器状态:" -ForegroundColor Yellow
$containers = @("course_management_db", "course_management_redis", "course_management_backend", "course_management_frontend")

foreach ($container in $containers) {
    $status = docker ps --filter "name=$container" --format "{{.Names}}: {{.Status}}"
    if ($status) {
        if ($status -like "*healthy*") {
            Write-Host "   ✅ $status" -ForegroundColor Green
        } elseif ($status -like "*Up*") {
            Write-Host "   🟡 $status" -ForegroundColor Yellow
        } else {
            Write-Host "   ❌ $status" -ForegroundColor Red
        }
    } else {
        Write-Host "   ❌ ${container}: 未运行" -ForegroundColor Red
    }
}

Write-Host ""

# 检查端口占用
Write-Host "🌐 端口状态检查:" -ForegroundColor Yellow
$ports = @(
    @{Port=5432; Service="PostgreSQL数据库"},
    @{Port=6379; Service="Redis缓存"},
    @{Port=8000; Service="Django后端"},
    @{Port=8081; Service="React前端"}
)

foreach ($portInfo in $ports) {
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $portInfo.Port -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-Host "   ✅ 端口 $($portInfo.Port): $($portInfo.Service) - 正常" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 端口 $($portInfo.Port): $($portInfo.Service) - 无响应" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ❌ 端口 $($portInfo.Port): $($portInfo.Service) - 检查失败" -ForegroundColor Red
    }
}

Write-Host ""

# 检查HTTP服务
Write-Host "🌍 HTTP服务检查:" -ForegroundColor Yellow

# 检查前端
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:8081" -Method Head -TimeoutSec 5
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "   ✅ 前端服务 (http://localhost:8081): 正常响应" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ 前端服务 (http://localhost:8081): 无法访问" -ForegroundColor Red
}

# 检查后端API
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -Method Get -TimeoutSec 5
    if ($backendResponse.StatusCode -eq 200) {
        $content = $backendResponse.Content | ConvertFrom-Json
        Write-Host "   ✅ 后端API (http://localhost:8000): $($content.message)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ 后端API (http://localhost:8000): 无法访问" -ForegroundColor Red
}

Write-Host ""

# 检查Docker资源使用
Write-Host "💻 资源使用情况:" -ForegroundColor Yellow
try {
    $stats = docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | Select-Object -Skip 1
    foreach ($line in $stats) {
        if ($line -and $line.Trim()) {
            Write-Host "   📊 $line" -ForegroundColor White
        }
    }
} catch {
    Write-Host "   ❌ 无法获取资源使用情况" -ForegroundColor Red
}

Write-Host ""

# 显示最近的日志
Write-Host "📝 最近的日志 (最后5行):" -ForegroundColor Yellow
Write-Host "   前端容器日志:" -ForegroundColor Cyan
try {
    $frontendLogs = docker logs course_management_frontend --tail 3 2>$null
    if ($frontendLogs) {
        $frontendLogs | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
    } else {
        Write-Host "     无日志或容器未运行" -ForegroundColor Gray
    }
} catch {
    Write-Host "     无法获取日志" -ForegroundColor Gray
}

Write-Host "   后端容器日志:" -ForegroundColor Cyan
try {
    $backendLogs = docker logs course_management_backend --tail 3 2>$null
    if ($backendLogs) {
        $backendLogs | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
    } else {
        Write-Host "     无日志或容器未运行" -ForegroundColor Gray
    }
} catch {
    Write-Host "     无法获取日志" -ForegroundColor Gray
}

Write-Host ""

# 显示快速操作提示
Write-Host "🛠️  快速操作:" -ForegroundColor Yellow
Write-Host "   重启所有服务: docker-compose restart" -ForegroundColor White
Write-Host "   查看完整日志: docker-compose logs -f" -ForegroundColor White
Write-Host "   停止所有服务: docker-compose down" -ForegroundColor White
Write-Host "   重新构建:     docker-compose up --build -d" -ForegroundColor White

Write-Host ""
Write-Host "检查完成！" -ForegroundColor Green
