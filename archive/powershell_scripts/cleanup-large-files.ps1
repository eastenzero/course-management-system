# 🧹 项目大文件清理脚本 - 清理70GB+的不必要文件
Write-Host "🧹 开始清理项目大文件..." -ForegroundColor Green

# 安全检查
if (-not (Test-Path ".git")) {
    Write-Host "❌ 当前目录不是Git仓库！" -ForegroundColor Red
    exit 1
}

# 显示当前磁盘使用情况
Write-Host "`n📊 当前磁盘使用情况分析:" -ForegroundColor Cyan
$totalSize = (Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
Write-Host "  总大小: $([math]::Round($totalSize / 1GB, 2)) GB" -ForegroundColor Yellow

# 分析各目录大小
Write-Host "`n📁 各目录大小分析:" -ForegroundColor Cyan
Get-ChildItem -Directory | ForEach-Object {
    $dirSize = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($dirSize -gt 100MB) {
        Write-Host "  📂 $($_.Name): $([math]::Round($dirSize / 1GB, 2)) GB" -ForegroundColor Gray
    }
}

# 询问用户确认
Write-Host "`n🚨 即将清理的内容:" -ForegroundColor Yellow
Write-Host "  1. 数据生成器输出文件 (JSON/SQL/CSV) - 约30GB" -ForegroundColor Red
Write-Host "  2. 临时备份文件 - 约0.7GB" -ForegroundColor Red  
Write-Host "  3. 虚拟环境目录 - 约0.4GB" -ForegroundColor Red
Write-Host "  4. Git LFS重复对象 (保留最新版本) - 约20GB" -ForegroundColor Red
Write-Host "  5. 临时和缓存文件" -ForegroundColor Red

$confirmation = Read-Host "`n⚠️  确认要清理这些文件吗？这将释放约50GB空间 (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "❌ 用户取消操作" -ForegroundColor Yellow
    exit 0
}

Write-Host "`n🧹 开始清理过程..." -ForegroundColor Green

# 1. 清理数据生成器输出文件
Write-Host "`n1️⃣ 清理数据生成器输出文件..." -ForegroundColor Yellow

$dataPatterns = @(
    "course-management-system/data-generator/*/json/*.json",
    "course-management-system/data-generator/*/sql/*.sql", 
    "course-management-system/course_data_output/*.json",
    "conservative_large_output/**/*.json",
    "conservative_large_output/**/*.sql",
    "optimized_large_output/**/*",
    "enhanced_huge_output/**/*"
)

$deletedDataSize = 0
foreach ($pattern in $dataPatterns) {
    $files = Get-ChildItem -Path $pattern -Recurse -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $deletedDataSize += $file.Length
        Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
        Write-Host "  🗑️  删除: $($file.Name)" -ForegroundColor Gray
    }
}
Write-Host "  ✅ 已删除数据文件: $([math]::Round($deletedDataSize / 1GB, 2)) GB" -ForegroundColor Green

# 2. 清理临时备份文件
Write-Host "`n2️⃣ 清理临时备份文件..." -ForegroundColor Yellow
$tempDirs = @("temp-backup", "temp_env")
$deletedTempSize = 0
foreach ($dir in $tempDirs) {
    if (Test-Path $dir) {
        $dirSize = (Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $deletedTempSize += $dirSize
        Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  🗑️  删除目录: $dir ($([math]::Round($dirSize / 1MB, 2)) MB)" -ForegroundColor Gray
    }
}
Write-Host "  ✅ 已删除临时文件: $([math]::Round($deletedTempSize / 1MB, 2)) MB" -ForegroundColor Green

# 3. 清理虚拟环境
Write-Host "`n3️⃣ 清理Python虚拟环境..." -ForegroundColor Yellow
$venvDirs = Get-ChildItem -Directory | Where-Object { $_.Name -like "*venv*" -or $_.Name -like "*env*" }
$deletedVenvSize = 0
foreach ($venv in $venvDirs) {
    $venvSize = (Get-ChildItem $venv.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $deletedVenvSize += $venvSize
    Remove-Item $venv.FullName -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  🗑️  删除虚拟环境: $($venv.Name) ($([math]::Round($venvSize / 1MB, 2)) MB)" -ForegroundColor Gray
}
Write-Host "  ✅ 已删除虚拟环境: $([math]::Round($deletedVenvSize / 1MB, 2)) MB" -ForegroundColor Green

# 4. 清理其他临时文件
Write-Host "`n4️⃣ 清理其他临时文件..." -ForegroundColor Yellow
$tempPatterns = @(
    "*.tmp",
    "*.temp", 
    "*.log",
    "__pycache__",
    "*.pyc",
    ".cache",
    "node_modules"
)

$deletedMiscSize = 0
foreach ($pattern in $tempPatterns) {
    $items = Get-ChildItem -Path $pattern -Recurse -Force -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            $itemSize = (Get-ChildItem $item.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $deletedMiscSize += $itemSize
            Remove-Item $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            $deletedMiscSize += $item.Length
            Remove-Item $item.FullName -Force -ErrorAction SilentlyContinue
        }
        Write-Host "  🗑️  删除: $($item.Name)" -ForegroundColor Gray
    }
}
Write-Host "  ✅ 已删除临时文件: $([math]::Round($deletedMiscSize / 1MB, 2)) MB" -ForegroundColor Green

# 5. 清理Git LFS重复对象
Write-Host "`n5️⃣ 清理Git LFS重复对象..." -ForegroundColor Yellow
$lfsObjsBefore = (Get-ChildItem ".git/lfs/objects" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
git lfs prune --dry-run | Out-Null
git lfs prune 2>$null
$lfsObjsAfter = (Get-ChildItem ".git/lfs/objects" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$lfsCleanedSize = $lfsObjsBefore - $lfsObjsAfter
Write-Host "  ✅ 已清理LFS对象: $([math]::Round($lfsCleanedSize / 1GB, 2)) GB" -ForegroundColor Green

# 6. Git垃圾回收
Write-Host "`n6️⃣ 执行Git垃圾回收..." -ForegroundColor Yellow
$gitBefore = (Get-ChildItem ".git" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
git gc --aggressive --prune=now 2>$null
$gitAfter = (Get-ChildItem ".git" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$gitCleanedSize = $gitBefore - $gitAfter
Write-Host "  ✅ Git垃圾回收完成: $([math]::Round($gitCleanedSize / 1MB, 2)) MB" -ForegroundColor Green

# 显示清理结果
Write-Host "`n📊 清理结果汇总:" -ForegroundColor Green
$totalCleaned = $deletedDataSize + $deletedTempSize + $deletedVenvSize + $deletedMiscSize + $lfsCleanedSize + $gitCleanedSize
$newTotalSize = (Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum

Write-Host "  📉 清理前大小: $([math]::Round($totalSize / 1GB, 2)) GB" -ForegroundColor Gray
Write-Host "  📈 清理后大小: $([math]::Round($newTotalSize / 1GB, 2)) GB" -ForegroundColor Gray  
Write-Host "  💾 释放空间: $([math]::Round($totalCleaned / 1GB, 2)) GB" -ForegroundColor Green
Write-Host "  📊 压缩比例: $([math]::Round((1 - $newTotalSize / $totalSize) * 100, 1))%" -ForegroundColor Green

Write-Host "`n🎯 保留的重要文件:" -ForegroundColor Cyan
Write-Host "  ✅ 源代码文件 (.py, .js, .html, .css)" -ForegroundColor Green
Write-Host "  ✅ 配置文件 (.yml, .json, .ini)" -ForegroundColor Green
Write-Host "  ✅ 文档文件 (.md, README*)" -ForegroundColor Green
Write-Host "  ✅ Docker配置文件" -ForegroundColor Green
Write-Host "  ✅ 关键备份文件 (通过LFS管理)" -ForegroundColor Green

Write-Host "`n🎉 清理完成！项目现在占用 $([math]::Round($newTotalSize / 1GB, 2)) GB" -ForegroundColor Green

# 更新.gitignore确保不再生成大文件
Write-Host "`n📝 更新.gitignore规则..." -ForegroundColor Yellow
$additionalIgnores = @"

# ===== 数据清理后的额外忽略规则 =====
# 防止重新生成大文件
**/data_output*/
**/conservative_large_output/
**/optimized_large_output/
**/enhanced_huge_output/
**/temp-backup/
**/temp_env/
*_venv/
**/*venv*/

# 临时和缓存文件
*.tmp
*.temp
.cache/
__pycache__/
*.pyc
*.pyo

"@

Add-Content -Path ".gitignore" -Value $additionalIgnores
Write-Host "  ✅ 已更新.gitignore防止重新生成大文件" -ForegroundColor Green

Write-Host "`n🚀 清理脚本执行完成！请检查项目功能是否正常。" -ForegroundColor Green
