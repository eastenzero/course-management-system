# 系统初始化脚本
$projectPath = "C:\Users\easten\Documents\G\eaten\qoder\0814\course-management-system"

Write-Host "=== 课程管理系统初始化 ===" -ForegroundColor Green
Set-Location $projectPath

Write-Host "1. 执行数据库迁移..." -ForegroundColor Yellow
docker compose exec backend python manage.py migrate

Write-Host "2. 收集静态文件..." -ForegroundColor Yellow  
docker compose exec backend python manage.py collectstatic --noinput

Write-Host "3. 检查数据库连接..." -ForegroundColor Yellow
docker compose exec backend python manage.py check --database default

Write-Host "4. 创建超级用户..." -ForegroundColor Yellow
Write-Host "请按照提示输入管理员信息："
docker compose exec -it backend python manage.py createsuperuser

Write-Host "5. 生成基础测试数据..." -ForegroundColor Yellow
if (Test-Path "create_basic_test_data.py") {
    docker compose exec backend python create_basic_test_data.py
} else {
    Write-Host "基础测试数据脚本不存在，跳过..." -ForegroundColor Red
}

Write-Host "6. 验证系统状态..." -ForegroundColor Yellow
Write-Host "检查服务状态："
docker compose ps

Write-Host "=== 初始化完成 ===" -ForegroundColor Green
Write-Host "访问地址："
Write-Host "  前端应用: http://localhost:18081" -ForegroundColor Cyan
Write-Host "  管理后台: http://localhost:18000/admin/" -ForegroundColor Cyan
Write-Host "  API文档: http://localhost:18000/api/schema/swagger-ui/" -ForegroundColor Cyan