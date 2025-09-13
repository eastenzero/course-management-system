# Git 双仓库同步管理脚本
# 使用方法：PowerShell -ExecutionPolicy Bypass -File git-dual-sync.ps1

param(
    [string]$Action = "status",  # status, push, pull, setup
    [string]$Branch = "main",
    [string]$Message = "",
    [switch]$Force = $false
)

function Show-Status {
    Write-Host "📊 Git仓库状态检查" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Gray
    
    Write-Host "`n📍 当前分支:" -ForegroundColor Cyan
    git branch --show-current
    
    Write-Host "`n📋 远程仓库:" -ForegroundColor Cyan
    git remote -v
    
    Write-Host "`n📦 本地状态:" -ForegroundColor Cyan
    git status --short
    
    Write-Host "`n🔄 分支同步状态:" -ForegroundColor Cyan
    git status --branch --porcelain=v1 | Select-Object -First 1
}

function Setup-DualRemote {
    Write-Host "🔧 设置双远程仓库同步" -ForegroundColor Green
    
    # 检查Gitea远程是否已存在
    $giteaExists = git remote | Select-String "gitea"
    if (-not $giteaExists) {
        $giteaUrl = "http://easten@192.168.100.176:13000/easten/course-management-system.git"
        Write-Host "ℹ️  使用默认Gitea URL: $giteaUrl" -ForegroundColor Cyan
        $customUrl = Read-Host "按Enter使用默认URL，或输入自定义URL"
        if ($customUrl) {
            $giteaUrl = $customUrl
        }
        git remote add gitea $giteaUrl
        Write-Host "✅ 已添加Gitea远程仓库" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Gitea远程仓库已存在" -ForegroundColor Yellow
    }
    
    # 配置origin同时推送到两个仓库
    $githubUrl = git remote get-url origin
    $giteaUrl = git remote get-url gitea
    
    Write-Host "🔄 配置同时推送..." -ForegroundColor Yellow
    git remote set-url --add --push origin $githubUrl
    git remote set-url --add --push origin $giteaUrl
    
    Write-Host "✅ 双远程配置完成！" -ForegroundColor Green
}

function Sync-Push {
    param([string]$branch, [string]$commitMessage)
    
    Write-Host "🚀 推送到双远程仓库" -ForegroundColor Green
    
    # 检查是否有未提交的更改
    $status = git status --porcelain
    if ($status -and $commitMessage) {
        Write-Host "📝 提交本地更改..." -ForegroundColor Yellow
        git add .
        git commit -m $commitMessage
    }
    
    # 推送到所有远程
    Write-Host "📤 推送到GitHub..." -ForegroundColor Cyan
    try {
        git push origin $branch
        Write-Host "✅ GitHub推送成功" -ForegroundColor Green
    } catch {
        Write-Host "❌ GitHub推送失败: $_" -ForegroundColor Red
    }
    
    Write-Host "📤 推送到Gitea..." -ForegroundColor Cyan
    try {
        git push gitea $branch
        Write-Host "✅ Gitea推送成功" -ForegroundColor Green
    } catch {
        Write-Host "❌ Gitea推送失败: $_" -ForegroundColor Red
        Write-Host "💡 请确保Gitea服务正在运行且仓库已创建" -ForegroundColor Yellow
    }
}

function Sync-Pull {
    param([string]$branch)
    
    Write-Host "📥 从远程仓库拉取更新" -ForegroundColor Green
    
    # 默认从GitHub拉取 (主要远程)
    Write-Host "📥 从GitHub拉取..." -ForegroundColor Cyan
    try {
        git pull origin $branch
        Write-Host "✅ GitHub拉取成功" -ForegroundColor Green
    } catch {
        Write-Host "❌ GitHub拉取失败: $_" -ForegroundColor Red
    }
}

# 主逻辑
switch ($Action.ToLower()) {
    "status" { Show-Status }
    "setup" { Setup-DualRemote }
    "push" { 
        if ($Message) {
            Sync-Push $Branch $Message 
        } else {
            Sync-Push $Branch ""
        }
    }
    "pull" { Sync-Pull $Branch }
    "sync" { 
        Sync-Pull $Branch
        if ($Message) {
            Sync-Push $Branch $Message
        } else {
            Sync-Push $Branch ""
        }
    }
    default {
        Write-Host "📖 Git双仓库同步工具使用说明" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Gray
        Write-Host ""
        Write-Host "用法: .\git-dual-sync.ps1 -Action <操作> [参数]" -ForegroundColor White
        Write-Host ""
        Write-Host "可用操作:" -ForegroundColor Cyan
        Write-Host "  status                  - 查看仓库状态" -ForegroundColor Gray
        Write-Host "  setup                   - 设置双远程仓库" -ForegroundColor Gray
        Write-Host "  pull                    - 从远程拉取更新" -ForegroundColor Gray  
        Write-Host "  push                    - 推送到双远程" -ForegroundColor Gray
        Write-Host "  sync                    - 拉取+推送" -ForegroundColor Gray
        Write-Host ""
        Write-Host "示例:" -ForegroundColor Cyan
        Write-Host "  .\git-dual-sync.ps1 -Action setup" -ForegroundColor Gray
        Write-Host "  .\git-dual-sync.ps1 -Action push -Message 'feat: 新功能'" -ForegroundColor Gray
        Write-Host "  .\git-dual-sync.ps1 -Action sync -Branch develop" -ForegroundColor Gray
    }
}