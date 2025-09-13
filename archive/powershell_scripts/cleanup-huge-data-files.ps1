# Deep cleanup for huge data files (remaining 30GB+)
Write-Host "Deep cleaning huge data files..." -ForegroundColor Green

# Find and remove the massive data files
Write-Host "`nFinding huge data files (>1GB)..." -ForegroundColor Cyan

$hugeFiles = Get-ChildItem -Recurse -File | Where-Object { 
    $_.Length -gt 1GB -and 
    ($_.Extension -eq ".json" -or $_.Extension -eq ".sql") -and
    $_.FullName -notlike "*\.git\*"
} | Sort-Object Length -Descending

Write-Host "Found $($hugeFiles.Count) huge data files:" -ForegroundColor Yellow
$totalHugeSize = 0
foreach ($file in $hugeFiles) {
    $sizeGB = [math]::Round($file.Length / 1GB, 2)
    $totalHugeSize += $file.Length
    Write-Host "  $($file.Name): $sizeGB GB" -ForegroundColor Red
}

Write-Host "`nTotal size of huge files: $([math]::Round($totalHugeSize / 1GB, 2)) GB" -ForegroundColor Yellow

$confirmation = Read-Host "`nDelete these huge data files? This will free ~$([math]::Round($totalHugeSize / 1GB, 2))GB (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Operation cancelled" -ForegroundColor Yellow
    exit 0
}

# Delete huge files
Write-Host "`nDeleting huge data files..." -ForegroundColor Yellow
$deletedHugeSize = 0
foreach ($file in $hugeFiles) {
    $size = $file.Length
    $deletedHugeSize += $size
    Remove-Item $file.FullName -Force
    Write-Host "  Deleted: $($file.Name) ($([math]::Round($size / 1GB, 2)) GB)" -ForegroundColor Green
}

# Clean empty directories
Write-Host "`nCleaning empty directories..." -ForegroundColor Yellow
$emptyDirs = Get-ChildItem -Recurse -Directory | Where-Object { 
    (Get-ChildItem $_.FullName -Recurse -Force | Measure-Object).Count -eq 0 
}
foreach ($dir in $emptyDirs) {
    Remove-Item $dir.FullName -Force -Recurse
    Write-Host "  Removed empty directory: $($dir.Name)" -ForegroundColor Gray
}

# Check final size
$finalSize = (Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum

Write-Host "`nDeep cleanup completed!" -ForegroundColor Green
Write-Host "  Huge files deleted: $([math]::Round($deletedHugeSize / 1GB, 2)) GB" -ForegroundColor Green
Write-Host "  Final project size: $([math]::Round($finalSize / 1GB, 2)) GB" -ForegroundColor Green

# Update .gitignore to prevent huge file generation
$preventHugeFiles = @"

# ===== Prevent huge file generation =====
# Block any files larger than 100MB
*.json
*.sql
*.csv
*.backup
*.dump

# Specific data output directories
**/data-generator/*/json/
**/data-generator/*/sql/
**/data_output*/
**/conservative_large_output/
**/optimized_large_output/
**/enhanced_huge_output/

"@

Add-Content -Path ".gitignore" -Value $preventHugeFiles
Write-Host "`nUpdated .gitignore to prevent huge file generation" -ForegroundColor Cyan

Write-Host "`nProject is now optimized and ready for use!" -ForegroundColor Green
