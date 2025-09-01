# Gitea Dual Repository Setup Script
Write-Host "Setting up dual Git repository sync (easten@192.168.100.176:13000)" -ForegroundColor Green

# Check if we're in a Git repository
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Current directory is not a Git repository!" -ForegroundColor Red
    exit 1
}

# Show current remote configuration
Write-Host "`nCurrent remote repository configuration:" -ForegroundColor Cyan
git remote -v

# Check if gitea remote already exists
$giteaExists = git remote | Select-String "gitea"
if ($giteaExists) {
    Write-Host "`nWARNING: Gitea remote already exists, updating configuration..." -ForegroundColor Yellow
    git remote remove gitea
}

# Add Gitea remote repository
$giteaUrl = "http://easten@192.168.100.176:13000/easten/course-management-system.git"
Write-Host "`nAdding Gitea remote repository: $giteaUrl" -ForegroundColor Yellow
git remote add gitea $giteaUrl

# Configure origin to push to both remotes
Write-Host "`nConfiguring origin to push to both GitHub and Gitea..." -ForegroundColor Yellow
$githubUrl = git remote get-url origin
git remote set-url --add --push origin $githubUrl
git remote set-url --add --push origin $giteaUrl

Write-Host "`nConfiguration completed!" -ForegroundColor Green
Write-Host "`nNew remote repository configuration:" -ForegroundColor Cyan
git remote -v

Write-Host "`nUsage:" -ForegroundColor White
Write-Host "  Push to all remotes: git push origin main" -ForegroundColor Gray
Write-Host "  Push to GitHub only: git push origin main (need to remove Gitea push URL)" -ForegroundColor Gray  
Write-Host "  Push to Gitea only:  git push gitea main" -ForegroundColor Gray
Write-Host "  SSH clone URL: ssh://easten@192.168.100.176:222/easten/course-management-system.git" -ForegroundColor Cyan
Write-Host "  Pull from GitHub: git pull origin main" -ForegroundColor Gray

Write-Host "`nIMPORTANT:" -ForegroundColor Yellow
Write-Host "  1. Make sure you have created 'course-management-system' repository in Gitea" -ForegroundColor Yellow
Write-Host "  2. Access URL: http://192.168.100.176:13000/" -ForegroundColor Yellow
Write-Host "  3. Username: easten / Password: ZhaYeFan05.07.14" -ForegroundColor Yellow
Write-Host "  4. You may need to enter Gitea credentials on first push" -ForegroundColor Yellow

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Create repository in Gitea" -ForegroundColor Gray
Write-Host "  2. Execute: git push origin main (push to both remotes)" -ForegroundColor Gray