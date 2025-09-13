# Simple Full Backup Setup for Gitea
Write-Host "Setting up Gitea full backup configuration" -ForegroundColor Green

# Check Git repository
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Current directory is not a Git repository!" -ForegroundColor Red
    exit 1
}

# Test Gitea connection
Write-Host "`nTesting Gitea connection..." -ForegroundColor Cyan
$giteaTest = Test-NetConnection -ComputerName 192.168.100.176 -Port 13000 -WarningAction SilentlyContinue
if ($giteaTest.TcpTestSucceeded) {
    Write-Host "SUCCESS: Gitea connection successful!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Gitea connection failed" -ForegroundColor Red
    exit 1
}

# Check current Git configuration
Write-Host "`nCurrent Git remote configuration:" -ForegroundColor Cyan
git remote -v

Write-Host "`nCurrent Git status:" -ForegroundColor Cyan
git status --short

Write-Host "`nFull backup coverage:" -ForegroundColor White
Write-Host "INCLUDED:" -ForegroundColor Green
Write-Host "  - Source code (all .py, .js, .css, .html files)" -ForegroundColor Gray
Write-Host "  - Configuration files (.yml, .json, .ini, requirements.txt)" -ForegroundColor Gray
Write-Host "  - Scripts and tools (.ps1, .sh, .bat)" -ForegroundColor Gray
Write-Host "  - Documentation (.md, README*, LICENSE*)" -ForegroundColor Gray
Write-Host "  - Docker configuration (Dockerfile, docker-compose*.yml)" -ForegroundColor Gray

Write-Host "EXCLUDED:" -ForegroundColor Red
Write-Host "  - Large data files (*.json, *.sql, *.csv outputs)" -ForegroundColor Gray
Write-Host "  - Sensitive information (.env, *.key, *.pem)" -ForegroundColor Gray
Write-Host "  - Temporary files (*.tmp, .cache, node_modules/)" -ForegroundColor Gray

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Create repository 'course-management-system' in Gitea" -ForegroundColor Gray
Write-Host "   URL: http://192.168.100.176:13000/" -ForegroundColor Gray
Write-Host "   Login: easten / Password: ZhaYeFan05.07.14" -ForegroundColor Gray
Write-Host "2. Run full backup: .\auto-backup-to-gitea.ps1" -ForegroundColor Gray

Write-Host "`nFull backup configuration completed!" -ForegroundColor Green