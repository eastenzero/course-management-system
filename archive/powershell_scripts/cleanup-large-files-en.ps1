# Project Large File Cleanup Script - Clean 70GB+ unnecessary files
Write-Host "Starting project large file cleanup..." -ForegroundColor Green

# Safety check
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Not in a Git repository!" -ForegroundColor Red
    exit 1
}

# Show current disk usage
Write-Host "`nCurrent disk usage analysis:" -ForegroundColor Cyan
$totalSize = (Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
Write-Host "  Total size: $([math]::Round($totalSize / 1GB, 2)) GB" -ForegroundColor Yellow

# Analyze directory sizes
Write-Host "`nDirectory size analysis:" -ForegroundColor Cyan
Get-ChildItem -Directory | ForEach-Object {
    $dirSize = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($dirSize -gt 100MB) {
        Write-Host "  $($_.Name): $([math]::Round($dirSize / 1GB, 2)) GB" -ForegroundColor Gray
    }
}

# Ask user confirmation
Write-Host "`nContent to be cleaned:" -ForegroundColor Yellow
Write-Host "  1. Data generator output files (JSON/SQL/CSV) - ~30GB" -ForegroundColor Red
Write-Host "  2. Temporary backup files - ~0.7GB" -ForegroundColor Red  
Write-Host "  3. Virtual environment directories - ~0.4GB" -ForegroundColor Red
Write-Host "  4. Git LFS duplicate objects (keep latest) - ~20GB" -ForegroundColor Red
Write-Host "  5. Temporary and cache files" -ForegroundColor Red

$confirmation = Read-Host "`nConfirm cleanup? This will free ~50GB space (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "User cancelled operation" -ForegroundColor Yellow
    exit 0
}

Write-Host "`nStarting cleanup process..." -ForegroundColor Green

# 1. Clean data generator output files
Write-Host "`n1. Cleaning data generator output files..." -ForegroundColor Yellow

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
        Write-Host "  Deleted: $($file.Name)" -ForegroundColor Gray
    }
}
Write-Host "  Deleted data files: $([math]::Round($deletedDataSize / 1GB, 2)) GB" -ForegroundColor Green

# 2. Clean temporary backup files
Write-Host "`n2. Cleaning temporary backup files..." -ForegroundColor Yellow
$tempDirs = @("temp-backup", "temp_env")
$deletedTempSize = 0
foreach ($dir in $tempDirs) {
    if (Test-Path $dir) {
        $dirSize = (Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $deletedTempSize += $dirSize
        Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Deleted directory: $dir ($([math]::Round($dirSize / 1MB, 2)) MB)" -ForegroundColor Gray
    }
}
Write-Host "  Deleted temp files: $([math]::Round($deletedTempSize / 1MB, 2)) MB" -ForegroundColor Green

# 3. Clean virtual environments
Write-Host "`n3. Cleaning Python virtual environments..." -ForegroundColor Yellow
$venvDirs = Get-ChildItem -Directory | Where-Object { $_.Name -like "*venv*" -or $_.Name -like "*env*" }
$deletedVenvSize = 0
foreach ($venv in $venvDirs) {
    $venvSize = (Get-ChildItem $venv.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $deletedVenvSize += $venvSize
    Remove-Item $venv.FullName -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  Deleted venv: $($venv.Name) ($([math]::Round($venvSize / 1MB, 2)) MB)" -ForegroundColor Gray
}
Write-Host "  Deleted virtual envs: $([math]::Round($deletedVenvSize / 1MB, 2)) MB" -ForegroundColor Green

# 4. Clean other temporary files
Write-Host "`n4. Cleaning other temporary files..." -ForegroundColor Yellow
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
        Write-Host "  Deleted: $($item.Name)" -ForegroundColor Gray
    }
}
Write-Host "  Deleted misc files: $([math]::Round($deletedMiscSize / 1MB, 2)) MB" -ForegroundColor Green

# 5. Clean Git LFS duplicate objects
Write-Host "`n5. Cleaning Git LFS duplicate objects..." -ForegroundColor Yellow
$lfsObjsBefore = (Get-ChildItem ".git/lfs/objects" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
git lfs prune --dry-run | Out-Null
git lfs prune 2>$null
$lfsObjsAfter = (Get-ChildItem ".git/lfs/objects" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$lfsCleanedSize = $lfsObjsBefore - $lfsObjsAfter
Write-Host "  Cleaned LFS objects: $([math]::Round($lfsCleanedSize / 1GB, 2)) GB" -ForegroundColor Green

# 6. Git garbage collection
Write-Host "`n6. Running Git garbage collection..." -ForegroundColor Yellow
$gitBefore = (Get-ChildItem ".git" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
git gc --aggressive --prune=now 2>$null
$gitAfter = (Get-ChildItem ".git" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$gitCleanedSize = $gitBefore - $gitAfter
Write-Host "  Git GC completed: $([math]::Round($gitCleanedSize / 1MB, 2)) MB" -ForegroundColor Green

# Show cleanup results
Write-Host "`nCleanup results summary:" -ForegroundColor Green
$totalCleaned = $deletedDataSize + $deletedTempSize + $deletedVenvSize + $deletedMiscSize + $lfsCleanedSize + $gitCleanedSize
$newTotalSize = (Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum

Write-Host "  Before cleanup: $([math]::Round($totalSize / 1GB, 2)) GB" -ForegroundColor Gray
Write-Host "  After cleanup: $([math]::Round($newTotalSize / 1GB, 2)) GB" -ForegroundColor Gray  
Write-Host "  Space freed: $([math]::Round($totalCleaned / 1GB, 2)) GB" -ForegroundColor Green
Write-Host "  Compression ratio: $([math]::Round((1 - $newTotalSize / $totalSize) * 100, 1))%" -ForegroundColor Green

Write-Host "`nImportant files kept:" -ForegroundColor Cyan
Write-Host "  Source code files (.py, .js, .html, .css)" -ForegroundColor Green
Write-Host "  Configuration files (.yml, .json, .ini)" -ForegroundColor Green
Write-Host "  Documentation files (.md, README*)" -ForegroundColor Green
Write-Host "  Docker configuration files" -ForegroundColor Green
Write-Host "  Key backup files (managed by LFS)" -ForegroundColor Green

Write-Host "`nCleanup completed! Project now uses $([math]::Round($newTotalSize / 1GB, 2)) GB" -ForegroundColor Green

# Update .gitignore to prevent regenerating large files
Write-Host "`nUpdating .gitignore rules..." -ForegroundColor Yellow
$additionalIgnores = @"

# ===== Additional ignore rules after cleanup =====
# Prevent regenerating large files
**/data_output*/
**/conservative_large_output/
**/optimized_large_output/
**/enhanced_huge_output/
**/temp-backup/
**/temp_env/
*_venv/
**/*venv*/

# Temporary and cache files
*.tmp
*.temp
.cache/
__pycache__/
*.pyc
*.pyo

"@

Add-Content -Path ".gitignore" -Value $additionalIgnores
Write-Host "  Updated .gitignore to prevent regenerating large files" -ForegroundColor Green

Write-Host "`nCleanup script completed! Please check if project functions normally." -ForegroundColor Green
