@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 校园课程管理系统 - 快速健康检查脚本 (Windows批处理版本)
:: 适用于Windows环境的简化版本

echo.
echo ================================================================
echo 🏫 校园课程管理系统 - 快速健康检查
echo ================================================================
echo.

:: 检查Docker是否安装
echo 🔍 检查系统先决条件...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Docker 未安装或未启动
    echo   💡 请先安装Docker Desktop并确保其正在运行
    pause
    exit /b 1
) else (
    echo   ✅ Docker 已安装
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Docker Compose 未安装
    echo   💡 请安装Docker Compose
    pause
    exit /b 1
) else (
    echo   ✅ Docker Compose 已安装
)

echo.
echo 🐳 检查Docker服务状态...
docker-compose ps >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Docker服务未运行，尝试启动...
    echo.
    echo 🚀 启动系统服务...
    docker-compose up -d
    if %errorlevel% neq 0 (
        echo   ❌ 启动失败，请检查docker-compose.yml文件
        pause
        exit /b 1
    )
    echo   服务启动中，等待15秒...
    timeout /t 15 /nobreak >nul
    
    echo.
    echo 🗄️  运行数据库迁移...
    docker-compose exec -T backend python manage.py migrate
    
    echo.
    echo 👤 创建测试用户...
    echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123', user_type='admin') if not User.objects.filter(username='admin').exists() else None; User.objects.create_user('teacher1', 'teacher1@example.com', 'teacher123', user_type='teacher', first_name='张', last_name='老师') if not User.objects.filter(username='teacher1').exists() else None; User.objects.create_user('student1', 'student1@example.com', 'student123', user_type='student', first_name='李', last_name='同学') if not User.objects.filter(username='student1').exists() else None; print('✅ 测试用户创建完成') | docker-compose exec -T backend python manage.py shell
) else (
    echo   ✅ Docker服务正在运行
)

echo.
echo 🔍 检查服务连接性...

:: 检查数据库端口
echo   检查数据库连接...
netstat -an | findstr ":5432" >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ PostgreSQL 端口 5432 可访问
    docker-compose exec -T db pg_isready -U postgres >nul 2>&1
    if %errorlevel% equ 0 (
        echo     ✅ PostgreSQL 数据库连接正常
    ) else (
        echo     ❌ PostgreSQL 数据库连接失败
    )
) else (
    echo     ❌ PostgreSQL 端口 5432 不可访问
)

:: 检查Redis端口
echo   检查Redis连接...
netstat -an | findstr ":6379" >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ Redis 端口 6379 可访问
    docker-compose exec -T redis redis-cli ping >nul 2>&1
    if %errorlevel% equ 0 (
        echo     ✅ Redis 连接正常
    ) else (
        echo     ❌ Redis 连接失败
    )
) else (
    echo     ❌ Redis 端口 6379 不可访问
)

:: 检查后端端口
echo   检查后端服务...
netstat -an | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ 后端端口 8000 可访问
    curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/health/ | findstr "200" >nul 2>&1
    if %errorlevel% equ 0 (
        echo     ✅ 后端健康检查通过
    ) else (
        echo     ❌ 后端健康检查失败
    )
) else (
    echo     ❌ 后端端口 8000 不可访问
)

:: 检查前端端口
echo   检查前端服务...
netstat -an | findstr ":8081" >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ 前端端口 8081 可访问
    curl -s -o nul -w "%%{http_code}" http://localhost:8081 | findstr "200" >nul 2>&1
    if %errorlevel% equ 0 (
        echo     ✅ 前端页面可访问
    ) else (
        echo     ❌ 前端页面不可访问
    )
) else (
    netstat -an | findstr ":3000" >nul 2>&1
    if %errorlevel% equ 0 (
        echo     ✅ 前端开发端口 3000 可访问
    ) else (
        echo     ❌ 前端服务不可访问
    )
)

echo.
echo ================================================================
echo 📊 系统状态总结
echo ================================================================
docker-compose ps

echo.
echo 📋 系统访问信息:
echo   🌐 前端应用: http://localhost:8081
echo   🔧 后端API: http://localhost:8000
echo   📚 API文档: http://localhost:8000/api/docs/
echo   👨‍💼 管理后台: http://localhost:8000/admin
echo.
echo 👤 测试账号:
echo   管理员: admin / admin123
echo   教师: teacher1 / teacher123
echo   学生: student1 / student123
echo.
echo 🔧 常用命令:
echo   查看服务状态: docker-compose ps
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo.
echo ✅ 健康检查完成！
echo.
pause
