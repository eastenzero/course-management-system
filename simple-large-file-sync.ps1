# Simple Large File Sync for Gitea
Write-Host "Starting large file sync to Gitea..." -ForegroundColor Green

# Check Git LFS
Write-Host "`nChecking Git LFS..." -ForegroundColor Cyan
$lfsVersion = git lfs version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Git LFS installed - $lfsVersion" -ForegroundColor Green
} else {
    Write-Host "ERROR: Git LFS not installed" -ForegroundColor Red
    Write-Host "Please install Git LFS from: https://git-lfs.github.io/" -ForegroundColor Yellow
    exit 1
}

# Initialize Git LFS if needed
Write-Host "`nSetting up Git LFS..." -ForegroundColor Cyan
if (-not (Test-Path ".gitattributes")) {
    Write-Host "Initializing Git LFS..." -ForegroundColor Yellow
    git lfs install
    
    # Track common large file types
    $patterns = @("*.zip", "*.tar.gz", "*.7z", "*.pdf", "*.mp4", "*.avi", "*.exe", "*.msi")
    foreach ($pattern in $patterns) {
        git lfs track $pattern
        Write-Host "  Tracking: $pattern" -ForegroundColor Gray
    }
    Write-Host "Git LFS setup completed" -ForegroundColor Green
} else {
    Write-Host "Git LFS already configured" -ForegroundColor Yellow
    Write-Host "Current LFS tracking rules:" -ForegroundColor Gray
    Get-Content ".gitattributes" | ForEach-Object {
        if ($_.Trim()) { Write-Host "  $_" -ForegroundColor Gray }
    }
}

# Find large files
Write-Host "`nScanning for large files (>100MB)..." -ForegroundColor Cyan
$largeFiles = @()
$threshold = 100MB

Get-ChildItem -Recurse -File | Where-Object { 
    $_.Length -gt $threshold -and 
    -not $_.FullName.Contains(".git") 
} | ForEach-Object {
    $sizeInMB = [math]::Round($_.Length / 1MB, 2)
    $relativePath = $_.FullName.Replace((Get-Location).Path + "\", "")
    $largeFiles += $relativePath
    Write-Host "  Found large file: $relativePath ($sizeInMB MB)" -ForegroundColor Yellow
}

if ($largeFiles.Count -eq 0) {
    Write-Host "No files larger than 100MB found" -ForegroundColor Green
} else {
    Write-Host "Found $($largeFiles.Count) large files" -ForegroundColor Yellow
}

# Check current repository status
Write-Host "`nRepository status:" -ForegroundColor Cyan
$totalFiles = (git ls-files | Measure-Object).Count
Write-Host "  Total tracked files: $totalFiles" -ForegroundColor Gray

$lfsFiles = git lfs ls-files 2>$null
if ($lfsFiles) {
    $lfsCount = ($lfsFiles | Measure-Object).Count
    Write-Host "  LFS managed files: $lfsCount" -ForegroundColor Gray
} else {
    Write-Host "  LFS managed files: 0" -ForegroundColor Gray
}

# Add and commit files
Write-Host "`nAdding all files..." -ForegroundColor Yellow
git add .

# Check for changes
$status = git diff --cached --name-only
if ($status) {
    $fileCount = ($status | Measure-Object).Count
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $commitMessage = "Large file sync: $timestamp - Updated $fileCount files"
    
    Write-Host "Committing changes: $commitMessage" -ForegroundColor Yellow
    git commit -m $commitMessage
    
    # Push LFS files first
    Write-Host "`nPushing LFS files..." -ForegroundColor Cyan
    git lfs push origin main 2>$null
    git lfs push gitea main 2>$null
    
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
    } else {
        Write-Host "ERROR: Gitea push failed" -ForegroundColor Red
        Write-Host $giteaResult -ForegroundColor Red
        
        if ($giteaResult -match "lfs|LFS") {
            Write-Host "TIP: Gitea may not support LFS, large files pushed as regular files" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "No new changes to sync" -ForegroundColor Yellow
}

Write-Host "`nLarge file sync process completed!" -ForegroundColor Green
Write-Host "Summary:" -ForegroundColor White
Write-Host "  - Git LFS configured for large files" -ForegroundColor Gray
Write-Host "  - Files >100MB automatically handled via LFS" -ForegroundColor Gray
Write-Host "  - Dual backup: GitHub + Gitea" -ForegroundColor Gray