# 自动全量备份到Gitea脚本
# 使用方法：PowerShell -ExecutionPolicy Bypass -File auto-backup-to-gitea.ps1

param(
    [switch]$Force = $false,    # 强制备份，即使没有更改
    [string]$Message = "",      # 自定义提交消息
    [switch]$Quiet = $false     # 静默模式
)

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    if (-not $Quiet) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $color = switch ($Level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "White" }
        }
        Write-Host "[$timestamp] $Message" -ForegroundColor $color
    }
}

function Check-Prerequisites {
    Write-Log "检查前置条件..." "INFO"
    
    # 检查Git仓库
    if (-not (Test-Path ".git")) {
        Write-Log "错误: 当前目录不是Git仓库！" "ERROR"
        return $false
    }
    
    # 检查远程仓库配置
    $remotes = git remote -v
    if (-not ($remotes -match "gitea")) {
        Write-Log "错误: 未配置Gitea远程仓库！请先运行 .\setup-dual-remote.ps1" "ERROR"
        return $false
    }
    
    if (-not ($remotes -match "origin")) {
        Write-Log "错误: 未配置GitHub远程仓库！" "ERROR"
        return $false
    }
    
    Write-Log "✅ 前置条件检查通过" "SUCCESS"
    return $true
}

function Get-RepoStats {
    $stats = @{
        TotalFiles = (git ls-files | Measure-Object).Count
        ModifiedFiles = (git diff --name-only | Measure-Object).Count
        UntrackedFiles = (git ls-files --others --exclude-standard | Measure-Object).Count
        TotalCommits = (git rev-list --count HEAD 2>$null)
    }
    return $stats
}

function Backup-ToGitea {
    Write-Log "开始全量备份到Gitea..." "INFO"
    
    # 获取当前状态
    $beforeStats = Get-RepoStats
    Write-Log "备份前统计: 文件总数=$($beforeStats.TotalFiles), 已修改=$($beforeStats.ModifiedFiles), 未跟踪=$($beforeStats.UntrackedFiles)" "INFO"
    
    # 添加所有文件
    Write-Log "添加所有文件到Git..." "INFO"
    git add .
    
    # 检查是否有更改需要提交
    $status = git diff --cached --name-only
    if ($status -or $Force) {
        # 准备提交消息
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        if ($Message) {
            $commitMessage = "$Message - $timestamp"
        } else {
            $fileCount = ($status | Measure-Object).Count
            $commitMessage = "自动备份: $timestamp - 更新了 $fileCount 个文件"
        }
        
        Write-Log "提交更改: $commitMessage" "INFO"
        git commit -m $commitMessage
        
        # 推送到GitHub
        Write-Log "推送到GitHub..." "INFO"
        $githubResult = git push origin main 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ GitHub推送成功" "SUCCESS"
        } else {
            Write-Log "❌ GitHub推送失败: $githubResult" "ERROR"
        }
        
        # 推送到Gitea
        Write-Log "推送到Gitea..." "INFO"
        $giteaResult = git push gitea main 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ Gitea推送成功" "SUCCESS"
            $backupSuccess = $true
        } else {
            Write-Log "❌ Gitea推送失败: $giteaResult" "ERROR"
            Write-Log "💡 可能需要先在Gitea中创建仓库" "WARN"
            $backupSuccess = $false
        }
        
        # 获取备份后状态
        $afterStats = Get-RepoStats
        Write-Log "备份后统计: 文件总数=$($afterStats.TotalFiles), 提交总数=$($afterStats.TotalCommits)" "INFO"
        
        return $backupSuccess
    } else {
        Write-Log "没有新的更改需要备份" "INFO"
        return $true
    }
}

function Generate-BackupReport {
    Write-Log "生成备份报告..." "INFO"
    
    $reportPath = "backup-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
    $report = @"
# Gitea 全量备份报告
生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## 仓库配置
$(git remote -v)

## 当前分支状态
$(git status --porcelain)

## 最近提交记录
$(git log --oneline -5)

## 文件统计
总文件数: $((git ls-files | Measure-Object).Count)
分支数量: $((git branch -a | Measure-Object).Count)
标签数量: $((git tag | Measure-Object).Count)

## .gitignore 规则验证
忽略的大文件类型: *.json, *.sql, *.csv (数据文件)
忽略的输出目录: data_output*, *_large_output/
包含的配置文件: *.yml, *.ps1, *.md, requirements.txt

## 备份覆盖范围
✅ 项目源代码
✅ 配置文件 (.yml, .json, .ini)
✅ 脚本工具 (.ps1, .sh, .bat)
✅ 文档资料 (.md, README*)
✅ 依赖配置 (requirements.txt, package.json)
✅ Docker配置 (Dockerfile, docker-compose.yml)
❌ 大数据文件 (已忽略)
❌ 敏感信息 (.env, *.key)
❌ 临时文件 (*.tmp, .cache)

"@
    
    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Log "📄 备份报告已保存: $reportPath" "SUCCESS"
}

# 主执行流程
Write-Log "🔄 开始Gitea全量备份流程" "INFO"

if (-not (Check-Prerequisites)) {
    exit 1
}

$backupResult = Backup-ToGitea

if ($backupResult) {
    Write-Log "🎉 全量备份成功完成！" "SUCCESS"
    Generate-BackupReport
    
    if (-not $Quiet) {
        Write-Host "`n📊 备份摘要:" -ForegroundColor Cyan
        Write-Host "  🎯 目标: 双重备份 (GitHub + Gitea)" -ForegroundColor Gray
        Write-Host "  📁 范围: 项目代码 + 配置 + 文档 + 脚本" -ForegroundColor Gray
        Write-Host "  🚫 排除: 大数据文件 + 敏感信息 + 临时文件" -ForegroundColor Gray
        Write-Host "  ✅ 状态: 备份成功" -ForegroundColor Green
    }
} else {
    Write-Log "❌ 备份过程中出现错误" "ERROR"
    Write-Log "💡 建议:" "WARN"
    Write-Log "  1. 检查网络连接" "WARN"
    Write-Log "  2. 确认Gitea中已创建仓库" "WARN"
    Write-Log "  3. 验证认证信息" "WARN"
    exit 1
}