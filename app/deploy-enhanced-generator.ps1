# 增强版数据生成器部署脚本
# PowerShell脚本用于部署和运行增强版百万级数据生成器

Write-Host "🚀 增强版百万级数据生成器部署" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# 设置工作目录
$workDir = "c:\Users\easten\Documents\G\eaten\qoder\0814\course-management-system"
Set-Location $workDir

Write-Host "📁 当前工作目录: $workDir" -ForegroundColor Yellow

# 检查Docker容器状态
Write-Host "🔍 检查Docker容器状态..." -ForegroundColor Yellow
docker-compose ps

# 复制增强版脚本到容器
Write-Host "`n📋 复制增强版脚本到容器..." -ForegroundColor Yellow
docker cp "backend\enhanced_million_generator.py" course_management_backend:/app/

# 验证文件复制成功
Write-Host "`n✅ 验证文件复制..." -ForegroundColor Yellow
docker-compose exec -T backend ls -la enhanced_million_generator.py

# 执行增强版数据生成
Write-Host "`n🎯 开始执行增强版数据生成..." -ForegroundColor Green
Write-Host "注意：此过程可能需要较长时间，请耐心等待" -ForegroundColor Red

# 运行增强版生成器
docker-compose exec backend python enhanced_million_generator.py

Write-Host "`n🎉 增强版数据生成器执行完成！" -ForegroundColor Green