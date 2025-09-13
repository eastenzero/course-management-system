# Docker启动脚本
$projectPath = "C:\Users\easten\Documents\G\eaten\qoder\0814\course-management-system"

Write-Host "切换到项目目录: $projectPath"
Set-Location $projectPath

Write-Host "当前目录: $(Get-Location)"

Write-Host "检查docker-compose.yml文件是否存在..."
if (Test-Path "docker-compose.yml") {
    Write-Host "✓ docker-compose.yml 文件存在"
    
    Write-Host "启动Docker服务..."
    docker compose up -d
    
    Write-Host "等待服务启动..."
    Start-Sleep 10
    
    Write-Host "检查服务状态..."
    docker compose ps
    
    Write-Host "检查容器日志..."
    docker compose logs
} else {
    Write-Host "✗ 找不到 docker-compose.yml 文件"
}