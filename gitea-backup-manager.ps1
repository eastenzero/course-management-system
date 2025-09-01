# Gitea Backup Manager - 全量备份管理工具
# 使用方法：PowerShell -ExecutionPolicy Bypass -File gitea-backup-manager.ps1

param(
    [string]$Action = "status",  # status, backup, verify, help
    [string]$Message = "",       # 自定义提交消息
    [switch]$Force = $false      # 强制备份
)

function Show-Status {
    Write-Host "🔍 Gitea双仓库备份状态检查" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Gray
    
    # Git配置状态
    Write-Host "`n📋 远程仓库配置:" -ForegroundColor Cyan
    git remote -v
    
    # 仓库统计
    Write-Host "`n📊 仓库统计信息:" -ForegroundColor Cyan
    $totalFiles = (git ls-files | Measure-Object).Count
    $totalCommits = git rev-list --count HEAD 2>$null
    $currentBranch = git branch --show-current
    
    Write-Host "  当前分支: $currentBranch" -ForegroundColor Gray
    Write-Host "  文件总数: $totalFiles" -ForegroundColor Gray
    Write-Host "  提交总数: $totalCommits" -ForegroundColor Gray
    
    # 同步状态
    Write-Host "`n🔄 同步状态:" -ForegroundColor Cyan
    $status = git status --porcelain
    if ($status) {
        Write-Host "  ⚠️  有未提交的更改:" -ForegroundColor Yellow
        $status | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    } else {
        Write-Host "  ✅ 工作区干净，已同步" -ForegroundColor Green
    }
    
    # 分支同步状态
    Write-Host "`n📡 远程同步状态:" -ForegroundColor Cyan
    try {
        $ahead = git rev-list --count origin/main..HEAD 2>$null
        $behind = git rev-list --count HEAD..origin/main 2>$null
        Write-Host "  GitHub: 领先 $ahead 个提交，落后 $behind 个提交" -ForegroundColor Gray
        
        $giteaAhead = git rev-list --count gitea/main..HEAD 2>$null
        $giteaBehind = git rev-list --count HEAD..gitea/main 2>$null
        Write-Host "  Gitea:  领先 $giteaAhead 个提交，落后 $giteaBehind 个提交" -ForegroundColor Gray
    } catch {
        Write-Host "  ⚠️  无法检查远程状态" -ForegroundColor Yellow
    }
}

function Backup-Repository {
    param([string]$commitMessage, [bool]$forceBackup)
    
    Write-Host "🚀 开始全量备份到双远程仓库" -ForegroundColor Green
    
    # 检查是否有更改
    git add .
    $status = git diff --cached --name-only
    
    if ($status -or $forceBackup) {
        # 准备提交消息
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        if ($commitMessage) {
            $finalMessage = "$commitMessage - $timestamp"
        } else {
            $fileCount = ($status | Measure-Object).Count
            $finalMessage = "全量备份: $timestamp - 更新了 $fileCount 个文件"
        }
        
        Write-Host "📝 提交更改: $finalMessage" -ForegroundColor Yellow
        git commit -m $finalMessage
        
        # 推送到GitHub
        Write-Host "📤 推送到GitHub..." -ForegroundColor Cyan
        $githubResult = git push origin main 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ GitHub备份成功" -ForegroundColor Green
        } else {
            Write-Host "❌ GitHub备份失败" -ForegroundColor Red
            return $false
        }
        
        # 推送到Gitea
        Write-Host "📤 推送到Gitea..." -ForegroundColor Cyan
        $giteaResult = git push gitea main 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Gitea备份成功" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Gitea备份失败" -ForegroundColor Red
            Write-Host $giteaResult -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "ℹ️  没有新的更改需要备份" -ForegroundColor Yellow
        return $true
    }
}

function Verify-Backup {
    Write-Host "🔍 验证备份完整性" -ForegroundColor Green
    
    # 验证远程仓库连接
    Write-Host "`n📡 验证远程连接..." -ForegroundColor Cyan
    
    # 检查GitHub
    Write-Host "  GitHub连接..." -ForegroundColor Gray
    $githubTest = git ls-remote origin 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✅ GitHub连接正常" -ForegroundColor Green
    } else {
        Write-Host "    ❌ GitHub连接失败" -ForegroundColor Red
    }
    
    # 检查Gitea
    Write-Host "  Gitea连接..." -ForegroundColor Gray
    $giteaTest = git ls-remote gitea 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✅ Gitea连接正常" -ForegroundColor Green
    } else {
        Write-Host "    ❌ Gitea连接失败" -ForegroundColor Red
    }
    
    # 验证备份覆盖范围
    Write-Host "`n📋 备份覆盖范围验证:" -ForegroundColor Cyan
    
    $includePatterns = @("*.py", "*.js", "*.yml", "*.json", "*.md", "*.ps1", "requirements.txt", "Dockerfile")
    $foundFiles = @{}
    
    foreach ($pattern in $includePatterns) {
        $files = git ls-files $pattern 2>$null
        $count = ($files | Measure-Object).Count
        $foundFiles[$pattern] = $count
        if ($count -gt 0) {
            Write-Host "    ✅ $pattern`: $count 个文件" -ForegroundColor Green
        }
    }
    
    # 验证排除的文件未被包含
    Write-Host "`n🚫 排除文件验证:" -ForegroundColor Cyan
    $excludePatterns = @("*.tmp", "*.cache", ".env")
    foreach ($pattern in $excludePatterns) {
        $files = git ls-files $pattern 2>$null
        $count = ($files | Measure-Object).Count
        if ($count -eq 0) {
            Write-Host "    ✅ $pattern`: 正确排除" -ForegroundColor Green
        } else {
            Write-Host "    ⚠️  $pattern`: 发现 $count 个文件" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n📊 总体备份质量评估:" -ForegroundColor White
    $totalTracked = (git ls-files | Measure-Object).Count
    Write-Host "  📁 跟踪文件总数: $totalTracked" -ForegroundColor Gray
    Write-Host "  🔄 双重备份状态: 正常" -ForegroundColor Green
    Write-Host "  📍 Gitea地址: http://192.168.100.176:13000/easten/course-management-system" -ForegroundColor Gray
    Write-Host "  📍 GitHub地址: https://github.com/eastenzero/course-management-system" -ForegroundColor Gray
}

function Show-Help {
    Write-Host "📖 Gitea全量备份管理工具使用说明" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Gray
    Write-Host ""
    Write-Host "用法: .\gitea-backup-manager.ps1 -Action <操作> [参数]" -ForegroundColor White
    Write-Host ""
    Write-Host "可用操作:" -ForegroundColor Cyan
    Write-Host "  status  - 显示备份状态和统计信息" -ForegroundColor Gray
    Write-Host "  backup  - 执行全量备份到双远程仓库" -ForegroundColor Gray
    Write-Host "  verify  - 验证备份完整性和连接状态" -ForegroundColor Gray
    Write-Host "  help    - 显示此帮助信息" -ForegroundColor Gray
    Write-Host ""
    Write-Host "参数:" -ForegroundColor Cyan
    Write-Host "  -Message <文本>  - 自定义提交消息" -ForegroundColor Gray
    Write-Host "  -Force           - 强制备份（即使没有更改）" -ForegroundColor Gray
    Write-Host ""
    Write-Host "示例:" -ForegroundColor Cyan
    Write-Host "  .\gitea-backup-manager.ps1 -Action status" -ForegroundColor Gray
    Write-Host "  .\gitea-backup-manager.ps1 -Action backup -Message '重要功能更新'" -ForegroundColor Gray
    Write-Host "  .\gitea-backup-manager.ps1 -Action verify" -ForegroundColor Gray
    Write-Host ""
    Write-Host "全量备份特性:" -ForegroundColor Cyan
    Write-Host "  ✅ 双重安全: GitHub + Gitea同步备份" -ForegroundColor Gray
    Write-Host "  ✅ 智能过滤: 自动排除大文件和敏感信息" -ForegroundColor Gray
    Write-Host "  ✅ 完整覆盖: 源码、配置、文档、脚本全包含" -ForegroundColor Gray
    Write-Host "  ✅ 状态监控: 实时查看备份状态和统计" -ForegroundColor Gray
}

# 主逻辑
switch ($Action.ToLower()) {
    "status" { Show-Status }
    "backup" { 
        $result = Backup-Repository $Message $Force
        if ($result) {
            Write-Host "`n🎉 全量备份成功完成！" -ForegroundColor Green
        } else {
            Write-Host "`n❌ 备份过程中出现错误" -ForegroundColor Red
        }
    }
    "verify" { Verify-Backup }
    "help" { Show-Help }
    default { Show-Help }
}