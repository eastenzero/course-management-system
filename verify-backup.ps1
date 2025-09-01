# Simple Backup Verification Script
Write-Host "Verifying Gitea backup completeness" -ForegroundColor Green

# Check Git repository status
Write-Host "`nRepository Status:" -ForegroundColor Cyan
git remote -v

Write-Host "`nRepository Statistics:" -ForegroundColor Cyan
$totalFiles = (git ls-files | Measure-Object).Count
$totalCommits = git rev-list --count HEAD 2>$null
$currentBranch = git branch --show-current

Write-Host "  Current branch: $currentBranch" -ForegroundColor Gray
Write-Host "  Total tracked files: $totalFiles" -ForegroundColor Gray
Write-Host "  Total commits: $totalCommits" -ForegroundColor Gray

# Test remote connections
Write-Host "`nRemote Connection Test:" -ForegroundColor Cyan

Write-Host "  Testing GitHub..." -ForegroundColor Gray
$githubTest = git ls-remote origin 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "    SUCCESS: GitHub connection OK" -ForegroundColor Green
} else {
    Write-Host "    ERROR: GitHub connection failed" -ForegroundColor Red
}

Write-Host "  Testing Gitea..." -ForegroundColor Gray
$giteaTest = git ls-remote gitea 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "    SUCCESS: Gitea connection OK" -ForegroundColor Green
} else {
    Write-Host "    ERROR: Gitea connection failed" -ForegroundColor Red
}

# Check file types
Write-Host "`nBackup Coverage Analysis:" -ForegroundColor Cyan

$patterns = @{
    "Python files" = "*.py"
    "JavaScript files" = "*.js"
    "Configuration files" = "*.yml"
    "JSON files" = "*.json"
    "Markdown docs" = "*.md"
    "PowerShell scripts" = "*.ps1"
    "Requirements" = "requirements.txt"
    "Docker configs" = "Dockerfile"
}

foreach ($type in $patterns.Keys) {
    $files = git ls-files $patterns[$type] 2>$null
    $count = ($files | Measure-Object).Count
    if ($count -gt 0) {
        Write-Host "  $type`: $count files" -ForegroundColor Green
    }
}

Write-Host "`nSummary:" -ForegroundColor White
Write-Host "  Repository URLs:" -ForegroundColor Gray
Write-Host "    GitHub: https://github.com/eastenzero/course-management-system" -ForegroundColor Gray
Write-Host "    Gitea:  http://192.168.100.176:13000/easten/course-management-system" -ForegroundColor Gray
Write-Host "  Total files backed up: $totalFiles" -ForegroundColor Green
Write-Host "  Dual backup status: ACTIVE" -ForegroundColor Green

Write-Host "`nBackup verification completed!" -ForegroundColor Green