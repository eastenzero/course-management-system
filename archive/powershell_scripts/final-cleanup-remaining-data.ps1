# Final cleanup for remaining large data files
Write-Host "Final cleanup of remaining large data files..." -ForegroundColor Green

# Find remaining JSON data files (but keep essential files)
$remainingDataFiles = Get-ChildItem -Recurse -File | Where-Object { 
    $_.Length -gt 100MB -and 
    ($_.Extension -eq ".json" -or $_.Extension -eq ".sql") -and
    $_.FullName -notlike "*\.git\*" -and
    $_.Name -like "*course_data*"
} | Sort-Object Length -Descending

if ($remainingDataFiles.Count -gt 0) {
    Write-Host "`nFound $($remainingDataFiles.Count) remaining large data files:" -ForegroundColor Yellow
    $totalRemaining = 0
    foreach ($file in $remainingDataFiles) {
        $sizeGB = [math]::Round($file.Length / 1GB, 2)
        $totalRemaining += $file.Length
        Write-Host "  $($file.Name): $sizeGB GB" -ForegroundColor Red
    }

    $confirmation = Read-Host "`nDelete remaining data files? This will free ~$([math]::Round($totalRemaining / 1GB, 2))GB (y/N)"
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        Write-Host "`nDeleting remaining data files..." -ForegroundColor Yellow
        foreach ($file in $remainingDataFiles) {
            $size = $file.Length
            Remove-Item $file.FullName -Force
            Write-Host "  Deleted: $($file.Name) ($([math]::Round($size / 1GB, 2)) GB)" -ForegroundColor Green
        }
    }
}

# Clean LFS cache more aggressively
Write-Host "`nCleaning LFS cache more aggressively..." -ForegroundColor Yellow
git lfs prune --verify-remote --verbose 2>$null

# Final size check
$finalSize = (Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum

Write-Host "`nFinal cleanup completed!" -ForegroundColor Green
Write-Host "Final project size: $([math]::Round($finalSize / 1GB, 2)) GB" -ForegroundColor Green

# Show what's taking up space now
Write-Host "`nRemaining large files (>100MB):" -ForegroundColor Cyan
Get-ChildItem -Recurse -File | Where-Object { $_.Length -gt 100MB } | Sort-Object Length -Descending | ForEach-Object {
    $type = if ($_.FullName -like "*\.git\lfs\*") { "LFS Object" } 
           elseif ($_.Extension -eq ".sqlite3") { "Database" }
           elseif ($_.Extension -eq ".tar.gz" -or $_.Extension -eq ".zip") { "Backup" }
           else { "Other" }
    Write-Host "  $($_.Name) - $([math]::Round($_.Length / 1MB, 2)) MB ($type)" -ForegroundColor Gray
}

Write-Host "`nProject cleanup is complete!" -ForegroundColor Green
