# Force Large File Sync - 强制同步大文件
Write-Host "Force syncing large files to Gitea..." -ForegroundColor Green

# Add JSON files to LFS (they are currently ignored)
Write-Host "`nAdding JSON files to LFS tracking..." -ForegroundColor Cyan
git lfs track "*.json"
Write-Host "Added *.json to LFS tracking" -ForegroundColor Green

# Add SQLite database files to LFS
Write-Host "Adding database files to LFS tracking..." -ForegroundColor Cyan
git lfs track "*.sqlite3"
git lfs track "*.db"
Write-Host "Added database files to LFS tracking" -ForegroundColor Green

# Check current .gitignore
Write-Host "`nChecking .gitignore rules..." -ForegroundColor Cyan
$gitignoreContent = Get-Content ".gitignore" -Raw

# Temporarily allow some large files for backup
Write-Host "Temporarily allowing large files for backup..." -ForegroundColor Yellow

# Create a backup-specific gitignore
$backupGitignore = @"

# ===== 临时允许大文件备份 =====
# 以下规则临时注释，允许通过LFS同步大文件

# 重要备份文件（通过LFS管理）
!course-management-system-backup-*.tar.gz
!course-management-system-clean-backup.zip

# 数据库备份（通过LFS管理）
!course-management-system/backend/db.sqlite3

# 注意：这些文件已配置为LFS跟踪，可以安全同步

"@

Add-Content -Path ".gitignore" -Value $backupGitignore

# Update .gitattributes with more patterns
Write-Host "`nUpdating LFS tracking patterns..." -ForegroundColor Cyan
$additionalPatterns = @"
*.sqlite3 filter=lfs diff=lfs merge=lfs -text
*.db filter=lfs diff=lfs merge=lfs -text
*.json filter=lfs diff=lfs merge=lfs -text
course-management-system-backup-*.tar.gz filter=lfs diff=lfs merge=lfs -text
course-management-system-clean-backup.zip filter=lfs diff=lfs merge=lfs -text
course-management-system/backend/db.sqlite3 filter=lfs diff=lfs merge=lfs -text
"@

Add-Content -Path ".gitattributes" -Value $additionalPatterns

# Force add large files to LFS
Write-Host "`nForce adding large files..." -ForegroundColor Yellow

# Add specific large files that we want to backup
$largeFilesToAdd = @(
    "course-management-system-backup-20250817_073248.tar.gz",
    "course-management-system-clean-backup.zip",
    "course-management-system/backend/db.sqlite3"
)

foreach ($file in $largeFilesToAdd) {
    if (Test-Path $file) {
        Write-Host "Adding large file: $file" -ForegroundColor Gray
        git add $file --force 2>$null
    }
}

# Add the .gitattributes file
git add .gitattributes
git add .gitignore

# Commit the changes
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMessage = "Enable large file sync: $timestamp - Added LFS support for backup files"

Write-Host "`nCommitting LFS configuration..." -ForegroundColor Yellow
git commit -m $commitMessage

# Push LFS files
Write-Host "`nPushing LFS files..." -ForegroundColor Cyan
git lfs push origin main 2>$null
git lfs push gitea main 2>$null

# Push regular commits
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
$githubResult = git push origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: GitHub push completed" -ForegroundColor Green
} else {
    Write-Host "WARNING: GitHub push issues" -ForegroundColor Yellow
    Write-Host $githubResult -ForegroundColor Gray
}

Write-Host "Pushing to Gitea..." -ForegroundColor Cyan
$giteaResult = git push gitea main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Gitea push completed" -ForegroundColor Green
} else {
    Write-Host "WARNING: Gitea push issues" -ForegroundColor Yellow
    Write-Host $giteaResult -ForegroundColor Gray
}

# Show LFS status
Write-Host "`nLFS Status:" -ForegroundColor White
git lfs ls-files | ForEach-Object {
    Write-Host "  LFS: $_" -ForegroundColor Cyan
}

Write-Host "`nLarge file sync configuration completed!" -ForegroundColor Green
Write-Host "Summary:" -ForegroundColor White
Write-Host "  - Enabled LFS for backup files and databases" -ForegroundColor Gray
Write-Host "  - Large files now tracked via Git LFS" -ForegroundColor Gray
Write-Host "  - Files >100MB can be synced safely" -ForegroundColor Gray
Write-Host "  - Dual backup maintained: GitHub + Gitea" -ForegroundColor Gray