# UI重新设计项目启动脚本
# 用于快速启动包含新UI美化功能的课程管理系统

Write-Host "🎨 启动UI重新设计版本的课程管理系统..." -ForegroundColor Cyan

# 检查Docker是否运行
Write-Host "检查Docker状态..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✅ Docker运行正常" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker未运行，请先启动Docker Desktop" -ForegroundColor Red
    exit 1
}

# 停止现有容器（如果有）
Write-Host "停止现有容器..." -ForegroundColor Yellow
docker-compose down

# 重新构建并启动所有服务
Write-Host "构建并启动所有服务..." -ForegroundColor Yellow
docker-compose up --build -d

# 等待服务启动
Write-Host "等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 检查服务状态
Write-Host "检查服务状态..." -ForegroundColor Yellow
$services = @(
    @{Name="数据库"; Url="http://localhost:5432"; Container="course_management_db"},
    @{Name="Redis"; Url="http://localhost:6379"; Container="course_management_redis"},
    @{Name="后端API"; Url="http://localhost:8000/api/health/"; Container="course_management_backend"},
    @{Name="前端界面"; Url="http://localhost:8081"; Container="course_management_frontend"}
)

foreach ($service in $services) {
    $status = docker ps --filter "name=$($service.Container)" --format "{{.Status}}"
    if ($status -like "*healthy*" -or $status -like "*Up*") {
        Write-Host "✅ $($service.Name): 运行正常" -ForegroundColor Green
    } else {
        Write-Host "❌ $($service.Name): 状态异常" -ForegroundColor Red
    }
}

# 测试前端连接
Write-Host "测试前端连接..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8081" -Method Head -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 前端服务响应正常" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 前端服务连接失败" -ForegroundColor Red
}

# 测试后端API
Write-Host "测试后端API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -Method Get -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 后端API响应正常" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 后端API连接失败" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 系统启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📱 访问地址:" -ForegroundColor Cyan
Write-Host "   前端界面: http://localhost:8081" -ForegroundColor White
Write-Host "   后端API:  http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "🎨 新功能特色:" -ForegroundColor Cyan
Write-Host "   ✨ 莫奈/莫兰迪主题系统" -ForegroundColor White
Write-Host "   ✨ 玻璃拟态效果组件" -ForegroundColor White
Write-Host "   ✨ 智能性能优化" -ForegroundColor White
Write-Host "   ✨ 完整无障碍支持" -ForegroundColor White
Write-Host "   ✨ 响应式设计" -ForegroundColor White
Write-Host ""
Write-Host "🔧 管理命令:" -ForegroundColor Cyan
Write-Host "   查看日志: docker-compose logs -f" -ForegroundColor White
Write-Host "   停止服务: docker-compose down" -ForegroundColor White
Write-Host "   重启服务: docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "🎯 演示页面:" -ForegroundColor Cyan
Write-Host "   UI展示: http://localhost:8081/demo/ui-redesign-showcase" -ForegroundColor White
Write-Host ""

# 询问是否打开浏览器
$openBrowser = Read-Host "是否打开浏览器查看界面？(y/n)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y" -or $openBrowser -eq "") {
    Write-Host "正在打开浏览器..." -ForegroundColor Yellow
    Start-Process "http://localhost:8081"
}

Write-Host "脚本执行完成！" -ForegroundColor Green
