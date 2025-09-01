# Simple Gitea Backup Script
Write-Host "Starting full backup to Gitea..." -ForegroundColor Green

# Check prerequisites
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Not a Git repository!" -ForegroundColor Red
    exit 1
}

# Check remote configuration
$remotes = git remote -v
if (-not ($remotes -match "gitea")) {
    Write-Host "ERROR: Gitea remote not configured!" -ForegroundColor Red
    Write-Host "Please run: .\setup-dual-remote.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Current repository stats:" -ForegroundColor Cyan
$totalFiles = (git ls-files | Measure-Object).Count
$modifiedFiles = (git diff --name-only | Measure-Object).Count
$untrackedFiles = (git ls-files --others --exclude-standard | Measure-Object).Count

Write-Host "  Total files: $totalFiles" -ForegroundColor Gray
Write-Host "  Modified files: $modifiedFiles" -ForegroundColor Gray
Write-Host "  Untracked files: $untrackedFiles" -ForegroundColor Gray

# Add all files
Write-Host "`nAdding all files to Git..." -ForegroundColor Yellow
git add .

# Check if there are changes to commit
$status = git diff --cached --name-only
if ($status) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $fileCount = ($status | Measure-Object).Count
    $commitMessage = "Auto backup: $timestamp - Updated $fileCount files"
    
    Write-Host "Committing changes: $commitMessage" -ForegroundColor Yellow
    git commit -m $commitMessage
    
    # Push to GitHub
    Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
    $githubResult = git push origin main 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: GitHub push completed" -ForegroundColor Green
    } else {
        Write-Host "ERROR: GitHub push failed" -ForegroundColor Red
        Write-Host $githubResult -ForegroundColor Red
    }
    
    # Push to Gitea
    Write-Host "Pushing to Gitea..." -ForegroundColor Cyan
    $giteaResult = git push gitea main 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: Gitea push completed" -ForegroundColor Green
        Write-Host "Full backup successful!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Gitea push failed" -ForegroundColor Red
        Write-Host $giteaResult -ForegroundColor Red
        Write-Host "TIP: Make sure you have created the repository in Gitea" -ForegroundColor Yellow
        Write-Host "URL: http://192.168.100.176:13000/" -ForegroundColor Yellow
    }
} else {
    Write-Host "No new changes to backup" -ForegroundColor Yellow
}

Write-Host "`nBackup coverage includes:" -ForegroundColor White
Write-Host "  - All source code files" -ForegroundColor Gray
Write-Host "  - Configuration files (.yml, .json, .ini)" -ForegroundColor Gray
Write-Host "  - Scripts and tools (.ps1, .sh, .bat)" -ForegroundColor Gray
Write-Host "  - Documentation (.md, README*)" -ForegroundColor Gray
Write-Host "  - Docker configuration" -ForegroundColor Gray
Write-Host "  - Dependencies (requirements.txt)" -ForegroundColor Gray

Write-Host "`nExcludes:" -ForegroundColor White
Write-Host "  - Large data files (per .gitignore)" -ForegroundColor Gray
Write-Host "  - Sensitive information (.env, *.key)" -ForegroundColor Gray
Write-Host "  - Temporary files (*.tmp, .cache)" -ForegroundColor Gray

Write-Host "`nFull backup process completed!" -ForegroundColor Green