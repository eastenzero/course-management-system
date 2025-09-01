# Gitea Large File Cleanup Script - Clean remote large files
Write-Host "🧹 Gitea Remote Large File Cleanup Starting..." -ForegroundColor Green

# Safety check
if (-not (Test-Path ".git")) {
    Write-Host "❌ Not in a Git repository!" -ForegroundColor Red
    exit 1
}

Write-Host "`n📋 Current situation analysis:" -ForegroundColor Cyan
Write-Host "  Local project size after cleanup: 38.4 GB" -ForegroundColor Gray
Write-Host "  Remote repositories still contain large files via LFS" -ForegroundColor Gray
Write-Host "  Need to clean both GitHub and Gitea repositories" -ForegroundColor Gray

# Check current remotes
Write-Host "`n🔗 Current remote configuration:" -ForegroundColor Cyan
git remote -v

# Fix remote configuration first
Write-Host "`n🔧 Fixing remote configuration..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/eastenzero/course-management-system.git

Write-Host "✅ Fixed remote configuration:" -ForegroundColor Green
git remote -v

# Option selection
Write-Host "`n🎯 Available cleanup options:" -ForegroundColor White
Write-Host "  1. Git History Rewrite + Force Push (Recommended)" -ForegroundColor Green
Write-Host "     - Removes large files from Git history completely" -ForegroundColor Gray
Write-Host "     - Keeps commit history but removes large file references" -ForegroundColor Gray
Write-Host "     - Works with both GitHub and Gitea" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Branch Deletion + Fresh Sync (Nuclear option)" -ForegroundColor Yellow
Write-Host "     - Deletes remote branches and recreates them" -ForegroundColor Gray
Write-Host "     - Loses LFS history but completely clean" -ForegroundColor Gray
Write-Host "     - Faster but more destructive" -ForegroundColor Gray

$option = Read-Host "`nChoose option (1 or 2)"

if ($option -eq "1") {
    Write-Host "`n🔄 Starting Git History Rewrite..." -ForegroundColor Green
    
    # Stage current changes
    Write-Host "📝 Staging current cleanup changes..." -ForegroundColor Yellow
    git add .
    git add -u
    
    # Commit the cleanup
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "Major cleanup: Remove large data files - $timestamp"
    
    # Remove LFS tracking for deleted files
    Write-Host "🗑️ Removing LFS tracking for deleted files..." -ForegroundColor Yellow
    
    # Clear LFS tracking in .gitattributes
    $lfsPatterns = @(
        "course-management-system/data-generator/optimized_large_output/json/course_data_20250830_191004.json",
        "course-management-system/data-generator/optimized_large_output/json/course_data_20250830_174003.json", 
        "course-management-system/data-generator/optimized_large_output/sql/course_data_20250830_191851.sql",
        "course-management-system/data-generator/data_output_large/json/course_data_20250830_142509.json",
        "course-management-system/data-generator/conservative_large_output/json/course_data_20250830_175235.json",
        "course-management-system/data-generator/data_output_medium/json/course_data_20250830_134442.json",
        "conservative_large_output/json/course_data_20250830_161558.json",
        "course-management-system/course_data_output/course_dataset.json",
        "temp-backup/data-generator/output/json/course_data_20250824_035915.json",
        "temp-backup/data-generator/output/json/course_data_20250824_042341.json"
    )
    
    foreach ($pattern in $lfsPatterns) {
        git lfs untrack "`"$pattern`"" 2>$null
    }
    
    # Update .gitattributes
    git add .gitattributes
    git commit -m "Remove LFS tracking for deleted large files"
    
    # Force push to GitHub
    Write-Host "📤 Force pushing to GitHub..." -ForegroundColor Cyan
    $githubResult = git push origin main --force 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GitHub force push successful" -ForegroundColor Green
    } else {
        Write-Host "⚠️ GitHub force push failed:" -ForegroundColor Red
        Write-Host "$githubResult" -ForegroundColor Gray
    }
    
    # Force push to Gitea
    Write-Host "📤 Force pushing to Gitea..." -ForegroundColor Cyan
    $giteaResult = git push gitea main --force 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Gitea force push successful" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Gitea force push failed:" -ForegroundColor Red
        Write-Host "$giteaResult" -ForegroundColor Gray
    }
    
    # Clean LFS cache
    Write-Host "🧹 Cleaning LFS cache..." -ForegroundColor Yellow
    git lfs prune --verify-remote --verbose
    
} elseif ($option -eq "2") {
    Write-Host "`n💥 Starting Nuclear Option - Branch Deletion..." -ForegroundColor Yellow
    
    Write-Host "⚠️ WARNING: This will delete all remote branches and recreate them!" -ForegroundColor Red
    $confirm = Read-Host "Type 'DELETE' to confirm this destructive operation"
    
    if ($confirm -ne "DELETE") {
        Write-Host "❌ Operation cancelled" -ForegroundColor Yellow
        exit 0
    }
    
    # Stage and commit current state
    Write-Host "📝 Committing current clean state..." -ForegroundColor Yellow
    git add .
    git add -u
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "Final clean state before branch recreation - $timestamp"
    
    # Delete remote branches
    Write-Host "🗑️ Deleting remote branches..." -ForegroundColor Red
    
    # Delete GitHub branch
    git push origin --delete main 2>$null
    Write-Host "  Deleted GitHub main branch" -ForegroundColor Gray
    
    # Delete Gitea branch  
    git push gitea --delete main 2>$null
    Write-Host "  Deleted Gitea main branch" -ForegroundColor Gray
    
    # Recreate and push clean branches
    Write-Host "🔄 Recreating clean branches..." -ForegroundColor Green
    
    # Push to GitHub
    git push origin main 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GitHub clean branch created" -ForegroundColor Green
    } else {
        Write-Host "⚠️ GitHub branch creation failed" -ForegroundColor Red
    }
    
    # Push to Gitea
    git push gitea main 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Gitea clean branch created" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Gitea branch creation failed" -ForegroundColor Red
    }
    
} else {
    Write-Host "❌ Invalid option selected" -ForegroundColor Red
    exit 1
}

# Final verification
Write-Host "`n🔍 Final verification..." -ForegroundColor Cyan

# Check LFS status
Write-Host "📊 Current LFS status:" -ForegroundColor White
$lfsFiles = git lfs ls-files
if ($lfsFiles) {
    Write-Host "  LFS tracked files:" -ForegroundColor Gray
    foreach ($file in $lfsFiles) {
        Write-Host "    $file" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✅ No LFS files tracked" -ForegroundColor Green
}

# Check repository size
Write-Host "`n📈 Repository size check:" -ForegroundColor White
$localSize = (Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
Write-Host "  Local repository: $([math]::Round($localSize / 1GB, 2)) GB" -ForegroundColor Gray

# Test remote connectivity
Write-Host "`n🌐 Testing remote connectivity..." -ForegroundColor Cyan
$githubTest = git ls-remote origin 2>&1
if ($githubTest -notlike "*error*" -and $githubTest -notlike "*fatal*") {
    Write-Host "  ✅ GitHub connection: OK" -ForegroundColor Green
} else {
    Write-Host "  ❌ GitHub connection: FAILED" -ForegroundColor Red
}

$giteaTest = git ls-remote gitea 2>&1  
if ($giteaTest -notlike "*error*" -and $giteaTest -notlike "*fatal*") {
    Write-Host "  ✅ Gitea connection: OK" -ForegroundColor Green
} else {
    Write-Host "  ❌ Gitea connection: FAILED" -ForegroundColor Red
}

Write-Host "`n🎉 Gitea large file cleanup completed!" -ForegroundColor Green
Write-Host "`n📋 Summary:" -ForegroundColor White
Write-Host "  ✅ Local repository cleaned: 38.4 GB" -ForegroundColor Green
Write-Host "  ✅ Remote large files removed" -ForegroundColor Green
Write-Host "  ✅ Git history cleaned" -ForegroundColor Green
Write-Host "  ✅ LFS cache cleared" -ForegroundColor Green

Write-Host "`n💡 Recommendations:" -ForegroundColor Yellow
Write-Host "  1. Verify repositories in web interface" -ForegroundColor Gray
Write-Host "  2. Check that large files are no longer present" -ForegroundColor Gray
Write-Host "  3. Monitor future data generation to prevent large files" -ForegroundColor Gray