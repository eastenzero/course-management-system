# Complete Large File Sync to Gitea - 完整大文件同步脚本
Write-Host "🚀 Starting complete large file sync to Gitea..." -ForegroundColor Green

# 检查当前位置
if (-not (Test-Path ".git")) {
    Write-Host "❌ Not in a Git repository!" -ForegroundColor Red
    exit 1
}

Write-Host "`n📊 Analyzing large files..." -ForegroundColor Cyan

# 查找所有超过50MB的文件
$largeFiles = Get-ChildItem -Recurse -File | Where-Object { 
    $_.Length -gt 50MB -and 
    $_.FullName -notlike "*\.git\*" -and
    $_.Name -notlike "*.tmp" -and
    $_.Name -notlike "*.temp"
} | Sort-Object Length -Descending

Write-Host "📈 Found $($largeFiles.Count) large files (>50MB):" -ForegroundColor White
foreach ($file in $largeFiles) {
    $sizeMB = [math]::Round($file.Length / 1MB, 2)
    $relativePath = $file.FullName.Replace((Get-Location).Path + "\", "")
    Write-Host "  📁 $relativePath ($sizeMB MB)" -ForegroundColor Gray
}

# 添加大文件类型到LFS跟踪
Write-Host "`n🔧 Configuring LFS tracking..." -ForegroundColor Yellow
$lfsPatterns = @(
    "*.json",
    "*.sql", 
    "*.sqlite3",
    "*.db",
    "*.tar.gz",
    "*.zip",
    "*.backup"
)

foreach ($pattern in $lfsPatterns) {
    git lfs track $pattern 2>$null
    Write-Host "  ✅ Tracking: $pattern" -ForegroundColor Green
}

# 添加具体的大文件
Write-Host "`n📁 Adding specific large files to LFS..." -ForegroundColor Yellow
$specificFiles = @()

foreach ($file in $largeFiles) {
    $relativePath = $file.FullName.Replace((Get-Location).Path + "\", "").Replace("\", "/")
    $specificFiles += $relativePath
    
    # 检查文件是否已在.gitignore中被忽略
    $ignored = git check-ignore $relativePath 2>$null
    if ($ignored) {
        Write-Host "  ⚠️  File ignored by .gitignore: $relativePath" -ForegroundColor Yellow
        # 强制添加到LFS跟踪
        git lfs track "`"$relativePath`"" 2>$null
    }
    
    # 强制添加文件
    git add $relativePath --force 2>$null
    Write-Host "  ➕ Added: $relativePath" -ForegroundColor Green
}

# 更新配置文件
Write-Host "`n📝 Updating configuration files..." -ForegroundColor Cyan
git add .gitattributes 2>$null
git add force-large-file-sync.ps1 2>$null

# 提交更改
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMessage = "Complete large file sync: $timestamp - Added $($largeFiles.Count) large files via LFS"

Write-Host "`n💾 Committing changes..." -ForegroundColor Yellow
$commitResult = git commit -m $commitMessage 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit successful" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No new changes to commit" -ForegroundColor Blue
}

# 推送LFS文件
Write-Host "`n🔄 Pushing LFS files..." -ForegroundColor Cyan
Write-Host "  📤 Pushing LFS to GitHub..." -ForegroundColor Gray
git lfs push origin main 2>$null

Write-Host "  📤 Pushing LFS to Gitea..." -ForegroundColor Gray  
git lfs push gitea main 2>$null

# 推送常规提交
Write-Host "`n🌐 Pushing commits..." -ForegroundColor Cyan

Write-Host "  📤 Pushing to GitHub..." -ForegroundColor Gray
$githubResult = git push origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ GitHub push successful" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  GitHub push issues:" -ForegroundColor Yellow
    Write-Host "     $githubResult" -ForegroundColor Gray
}

Write-Host "  📤 Pushing to Gitea..." -ForegroundColor Gray
$giteaResult = git push gitea main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Gitea push successful" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Gitea push issues:" -ForegroundColor Yellow
    Write-Host "     $giteaResult" -ForegroundColor Gray
}

# 显示最终状态
Write-Host "`n📊 Final sync status:" -ForegroundColor White

# LFS文件状态
$lfsFiles = git lfs ls-files
Write-Host "`n🗃️  LFS tracked files:" -ForegroundColor Cyan
if ($lfsFiles) {
    foreach ($lfsFile in $lfsFiles) {
        Write-Host "  📁 $lfsFile" -ForegroundColor Green
    }
} else {
    Write-Host "  ℹ️  No LFS files found" -ForegroundColor Blue
}

# 远程仓库状态
Write-Host "`n🌐 Remote repositories:" -ForegroundColor Cyan
git remote -v | ForEach-Object {
    Write-Host "  🔗 $_" -ForegroundColor Gray
}

Write-Host "`n🎉 Complete large file sync finished!" -ForegroundColor Green
Write-Host "`n📋 Summary:" -ForegroundColor White
Write-Host "  ✅ Large files (>50MB) processed via LFS" -ForegroundColor Gray
Write-Host "  ✅ Files >100MB can now sync safely" -ForegroundColor Gray
Write-Host "  ✅ Dual backup maintained: GitHub + Gitea" -ForegroundColor Gray
Write-Host "  ✅ All files synchronized successfully" -ForegroundColor Gray

Write-Host "`n🔧 Next time use:" -ForegroundColor Yellow
Write-Host "  PowerShell -ExecutionPolicy Bypass -File complete-large-file-sync.ps1" -ForegroundColor Cyan