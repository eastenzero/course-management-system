# Gitea 全量备份配置脚本
# 使用方法：PowerShell -ExecutionPolicy Bypass -File gitea-full-backup-setup.ps1

param(
    [string]$Action = "setup",  # setup, create-repo, test-push, backup-all
    [string]$RepoName = "course-management-system"
)

$giteaHost = "192.168.100.176"
$giteaPort = 13000
$giteaUser = "easten"
$giteaPassword = "ZhaYeFan05.07.14"
$giteaUrl = "http://$giteaHost`:$giteaPort"

Write-Host "🔧 Gitea 全量备份配置工具" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Gray

function Test-GiteaConnection {
    Write-Host "`n📡 测试Gitea连接..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri $giteaUrl -Method Head -TimeoutSec 10 -ErrorAction Stop
        Write-Host "✅ Gitea服务连接成功！" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Gitea服务连接失败: $_" -ForegroundColor Red
        return $false
    }
}

function Create-GiteaRepo {
    Write-Host "`n📝 创建Gitea仓库指导..." -ForegroundColor Cyan
    Write-Host "请手动执行以下步骤：" -ForegroundColor Yellow
    Write-Host "1. 访问: $giteaUrl" -ForegroundColor Gray
    Write-Host "2. 登录账号: $giteaUser" -ForegroundColor Gray
    Write-Host "3. 点击右上角 '+' -> '新建仓库'" -ForegroundColor Gray
    Write-Host "4. 仓库名称: $RepoName" -ForegroundColor Gray
    Write-Host "5. 设置为公开或私有（推荐私有）" -ForegroundColor Gray
    Write-Host "6. 不要初始化README、.gitignore或License" -ForegroundColor Gray
    Write-Host "7. 点击'创建仓库'" -ForegroundColor Gray
    
    $confirm = Read-Host "`n已完成仓库创建？(y/n)"
    return $confirm -eq "y" -or $confirm -eq "Y"
}

function Test-GitPush {
    Write-Host "`n🚀 测试Git推送..." -ForegroundColor Cyan
    
    # 检查是否在Git仓库中
    if (-not (Test-Path ".git")) {
        Write-Host "❌ 当前目录不是Git仓库！" -ForegroundColor Red
        return $false
    }
    
    # 检查gitea远程是否存在
    $remotes = git remote -v
    if ($remotes -match "gitea") {
        Write-Host "✅ Gitea远程仓库已配置" -ForegroundColor Green
        
        # 尝试推送
        Write-Host "正在推送到Gitea..." -ForegroundColor Yellow
        try {
            git push gitea main 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Gitea推送成功！" -ForegroundColor Green
                return $true
            } else {
                Write-Host "❌ Gitea推送失败" -ForegroundColor Red
                return $false
            }
        } catch {
            Write-Host "❌ 推送出错: $_" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ 未配置Gitea远程仓库，请先运行 .\setup-dual-remote.ps1" -ForegroundColor Red
        return $false
    }
}

function Setup-FullBackup {
    Write-Host "`n🗄️ 配置全量备份策略..." -ForegroundColor Cyan
    
    # 确保.gitignore不会排除重要的配置文件
    $gitignorePath = ".gitignore"
    if (Test-Path $gitignorePath) {
        Write-Host "📋 检查.gitignore配置..." -ForegroundColor Yellow
        
        # 读取当前.gitignore
        $content = Get-Content $gitignorePath -Raw
        
        # 确保备份重要文件
        $backupRules = @"

# ===== 全量备份配置 =====
# 确保重要配置文件被备份
!*.md
!*.yml
!*.yaml
!*.json
!*.ini
!*.conf
!*.config
!requirements.txt
!package.json
!Dockerfile
!docker-compose*.yml
!.env.example

# 备份脚本和工具
!*.ps1
!*.sh
!*.bat

# 备份文档
!docs/
!README*
!CHANGELOG*
!LICENSE*

# 但是排除敏感信息
.env
*.key
*.pem
secrets/
credentials/

# 排除临时和缓存文件
*.tmp
*.temp
*.cache
.DS_Store
Thumbs.db

"@
        
        if (-not $content.Contains("# ===== 全量备份配置 =====")) {
            Add-Content -Path $gitignorePath -Value $backupRules
            Write-Host "✅ 已更新.gitignore以支持全量备份" -ForegroundColor Green
        } else {
            Write-Host "ℹ️ .gitignore已包含备份配置" -ForegroundColor Yellow
        }
    }
    
    Write-Host "✅ 全量备份配置完成！" -ForegroundColor Green
}

function Show-BackupStatus {
    Write-Host "`n📊 备份状态检查..." -ForegroundColor Cyan
    
    if (Test-Path ".git") {
        Write-Host "📋 Git远程仓库配置:" -ForegroundColor White
        git remote -v
        
        Write-Host "`n📈 仓库统计:" -ForegroundColor White
        $fileCount = (git ls-files | Measure-Object).Count
        $commitCount = (git rev-list --count HEAD 2>$null)
        $branchCount = (git branch -r | Measure-Object).Count
        
        Write-Host "  文件数量: $fileCount" -ForegroundColor Gray
        Write-Host "  提交数量: $commitCount" -ForegroundColor Gray
        Write-Host "  远程分支: $branchCount" -ForegroundColor Gray
        
        Write-Host "`n🔄 同步状态:" -ForegroundColor White
        git status --porcelain | ForEach-Object {
            if ($_.StartsWith("??")) {
                Write-Host "  未跟踪: $($_.Substring(3))" -ForegroundColor Yellow
            } elseif ($_.StartsWith(" M")) {
                Write-Host "  已修改: $($_.Substring(3))" -ForegroundColor Cyan
            }
        }
    } else {
        Write-Host "❌ 当前目录不是Git仓库" -ForegroundColor Red
    }
}

function Backup-All {
    Write-Host "`n🔄 执行全量备份..." -ForegroundColor Cyan
    
    # 添加所有文件（除了.gitignore排除的）
    Write-Host "添加所有跟踪文件..." -ForegroundColor Yellow
    git add .
    
    # 检查是否有更改
    $status = git status --porcelain
    if ($status) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $commitMessage = "备份更新: $timestamp - 全量同步到Gitea"
        
        Write-Host "提交更改..." -ForegroundColor Yellow
        git commit -m $commitMessage
        
        Write-Host "推送到所有远程仓库..." -ForegroundColor Yellow
        git push origin main
        git push gitea main
        
        Write-Host "✅ 全量备份完成！" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ 没有需要备份的新更改" -ForegroundColor Yellow
    }
}

# 主逻辑
switch ($Action.ToLower()) {
    "setup" {
        if (Test-GiteaConnection) {
            Setup-FullBackup
            Show-BackupStatus
            Write-Host "`n🎯 下一步操作:" -ForegroundColor Cyan
            Write-Host "  1. 创建仓库: .\gitea-full-backup-setup.ps1 -Action create-repo" -ForegroundColor Gray
            Write-Host "  2. 测试推送: .\gitea-full-backup-setup.ps1 -Action test-push" -ForegroundColor Gray
            Write-Host "  3. 执行备份: .\gitea-full-backup-setup.ps1 -Action backup-all" -ForegroundColor Gray
        }
    }
    "create-repo" {
        if (Test-GiteaConnection) {
            Create-GiteaRepo
        }
    }
    "test-push" {
        Test-GitPush
    }
    "backup-all" {
        Backup-All
    }
    default {
        Write-Host "📖 Gitea全量备份工具使用说明" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Gray
        Write-Host ""
        Write-Host "用法: .\gitea-full-backup-setup.ps1 -Action <操作>" -ForegroundColor White
        Write-Host ""
        Write-Host "可用操作:" -ForegroundColor Cyan
        Write-Host "  setup       - 初始配置全量备份" -ForegroundColor Gray
        Write-Host "  create-repo - 创建Gitea仓库指导" -ForegroundColor Gray
        Write-Host "  test-push   - 测试推送到Gitea" -ForegroundColor Gray  
        Write-Host "  backup-all  - 执行全量备份" -ForegroundColor Gray
        Write-Host ""
        Write-Host "全量备份特性:" -ForegroundColor Cyan
        Write-Host "  ✅ 备份所有配置文件" -ForegroundColor Gray
        Write-Host "  ✅ 备份脚本和工具" -ForegroundColor Gray
        Write-Host "  ✅ 备份文档和说明" -ForegroundColor Gray
        Write-Host "  ✅ 双重安全保障" -ForegroundColor Gray
        Write-Host "  ❌ 排除敏感信息" -ForegroundColor Gray
        Write-Host "  ❌ 排除临时文件" -ForegroundColor Gray
    }
}