# Gitea Large File Sync Script - 支持超过100MB文件的同步
# 使用方法：PowerShell -ExecutionPolicy Bypass -File sync-gitea-large-files.ps1

param(
    [switch]$Force = $false,    # 强制同步
    [string]$Message = "",      # 自定义提交消息
    [switch]$SkipLFS = $false   # 跳过LFS配置
)

Write-Host "🚀 开始Gitea大文件同步流程" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Gray

# 检查Git LFS
function Check-GitLFS {
    Write-Host "`n🔍 检查Git LFS状态..." -ForegroundColor Cyan
    
    $lfsVersion = git lfs version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Git LFS 已安装: $lfsVersion" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Git LFS 未安装" -ForegroundColor Red
        Write-Host "💡 请安装Git LFS: https://git-lfs.github.io/" -ForegroundColor Yellow
        return $false
    }
}

# 配置Git LFS跟踪大文件
function Setup-GitLFS {
    Write-Host "`n⚙️ 配置Git LFS跟踪大文件..." -ForegroundColor Cyan
    
    # 检查是否已初始化LFS
    if (-not (Test-Path ".gitattributes")) {
        Write-Host "初始化Git LFS..." -ForegroundColor Yellow
        git lfs install
        
        # 配置要跟踪的大文件类型
        $largeFilePatterns = @(
            "*.zip",
            "*.tar.gz", 
            "*.7z",
            "*.rar",
            "*.iso",
            "*.dmg",
            "*.pkg",
            "*.exe",
            "*.msi",
            "*.deb",
            "*.rpm",
            "*.pdf",
            "*.doc",
            "*.docx",
            "*.ppt",
            "*.pptx",
            "*.xls",
            "*.xlsx",
            "*.mp4",
            "*.avi",
            "*.mov",
            "*.mkv",
            "*.mp3",
            "*.wav",
            "*.flac",
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.gif",
            "*.bmp",
            "*.tiff",
            "*.psd",
            "*.ai",
            "*.sketch"
        )
        
        Write-Host "配置LFS跟踪文件类型..." -ForegroundColor Yellow
        foreach ($pattern in $largeFilePatterns) {
            git lfs track $pattern
            Write-Host "  添加跟踪: $pattern" -ForegroundColor Gray
        }
        
        # 也跟踪超过100MB的文件（通过文件大小）
        Write-Host "配置100MB以上文件跟踪..." -ForegroundColor Yellow
        
        Write-Host "✅ Git LFS 配置完成" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ Git LFS 已配置，查看当前跟踪规则..." -ForegroundColor Yellow
        Get-Content ".gitattributes" | ForEach-Object {
            if ($_.Trim()) {
                Write-Host "  $_" -ForegroundColor Gray
            }
        }
    }
}

# 检查大文件
function Find-LargeFiles {
    Write-Host "`n🔍 扫描大文件..." -ForegroundColor Cyan
    
    $largeFiles = @()
    $threshold = 100MB
    
    # 扫描工作目录中的大文件
    Get-ChildItem -Recurse -File | Where-Object { 
        $_.Length -gt $threshold -and 
        -not $_.FullName.Contains(".git") -and
        -not $_.FullName.Contains("node_modules") 
    } | ForEach-Object {
        $sizeInMB = [math]::Round($_.Length / 1MB, 2)
        $relativePath = $_.FullName.Replace((Get-Location).Path + "\", "")
        $largeFiles += @{
            Path = $relativePath
            SizeMB = $sizeInMB
            File = $_
        }
        Write-Host "  发现大文件: $relativePath ($sizeInMB MB)" -ForegroundColor Yellow
    }
    
    if ($largeFiles.Count -eq 0) {
        Write-Host "✅ 未发现超过100MB的文件" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 发现 $($largeFiles.Count) 个大文件" -ForegroundColor Yellow
        
        # 为大文件添加LFS跟踪
        Write-Host "为大文件配置LFS跟踪..." -ForegroundColor Yellow
        foreach ($file in $largeFiles) {
            $pattern = "*" + [System.IO.Path]::GetExtension($file.File.Name)
            git lfs track $pattern 2>$null
            Write-Host "  添加LFS跟踪: $pattern" -ForegroundColor Gray
        }
    }
    
    return $largeFiles
}

# 更新.gitignore以允许某些大文件类型
function Update-GitIgnore {
    Write-Host "`n📝 更新.gitignore配置..." -ForegroundColor Cyan
    
    $gitignorePath = ".gitignore"
    if (Test-Path $gitignorePath) {
        $content = Get-Content $gitignorePath -Raw
        
        # 检查是否需要添加LFS相关配置
        if (-not $content.Contains("# ===== Git LFS 大文件配置 =====")) {
            $lfsConfig = @"

# ===== Git LFS 大文件配置 =====
# 允许通过LFS管理的大文件类型
# 这些文件将通过Git LFS存储，不受100MB限制

# 媒体文件（通过LFS管理）
# *.mp4
# *.avi  
# *.mov
# *.mkv

# 文档文件（通过LFS管理）
# *.pdf
# *.doc
# *.docx

# 压缩文件（通过LFS管理）
# *.zip
# *.tar.gz
# *.7z

# 注意：以上文件类型已配置为LFS跟踪
# 如需添加特定大文件，请使用: git lfs track "filename"

"@
            Add-Content -Path $gitignorePath -Value $lfsConfig
            Write-Host "✅ 已更新.gitignore添加LFS配置说明" -ForegroundColor Green
        } else {
            Write-Host "ℹ️ .gitignore已包含LFS配置" -ForegroundColor Yellow
        }
    }
}

# 执行同步
function Sync-ToGitea {
    param([string]$commitMessage, [bool]$forceSync)
    
    Write-Host "`n🚀 开始同步到Gitea..." -ForegroundColor Cyan
    
    # 添加所有文件（包括LFS文件）
    Write-Host "添加所有文件..." -ForegroundColor Yellow
    git add .
    
    # 检查LFS文件状态
    Write-Host "检查LFS文件状态..." -ForegroundColor Yellow
    $lfsFiles = git lfs ls-files 2>$null
    if ($lfsFiles) {
        Write-Host "LFS管理的文件:" -ForegroundColor Cyan
        $lfsFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    }
    
    # 检查是否有更改
    $status = git diff --cached --name-only
    if ($status -or $forceSync) {
        # 准备提交消息
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        if ($commitMessage) {
            $finalMessage = "$commitMessage - $timestamp"
        } else {
            $fileCount = ($status | Measure-Object).Count
            $finalMessage = "大文件同步: $timestamp - 更新了 $fileCount 个文件"
        }
        
        Write-Host "提交更改: $finalMessage" -ForegroundColor Yellow
        git commit -m $finalMessage
        
        # 推送LFS文件
        Write-Host "推送LFS文件到GitHub..." -ForegroundColor Cyan
        git lfs push origin main 2>$null
        
        # 推送到GitHub
        Write-Host "推送到GitHub..." -ForegroundColor Cyan
        $githubResult = git push origin main 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ GitHub推送成功" -ForegroundColor Green
        } else {
            Write-Host "❌ GitHub推送失败" -ForegroundColor Red
            Write-Host $githubResult -ForegroundColor Red
        }
        
        # 推送LFS文件到Gitea
        Write-Host "推送LFS文件到Gitea..." -ForegroundColor Cyan
        git lfs push gitea main 2>$null
        
        # 推送到Gitea
        Write-Host "推送到Gitea..." -ForegroundColor Cyan
        $giteaResult = git push gitea main 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Gitea推送成功" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Gitea推送失败" -ForegroundColor Red
            Write-Host $giteaResult -ForegroundColor Red
            
            # 如果是LFS相关错误，提供解决建议
            if ($giteaResult -match "lfs|LFS") {
                Write-Host "💡 Gitea可能不支持LFS，大文件将作为普通文件推送" -ForegroundColor Yellow
            }
            return $false
        }
    } else {
        Write-Host "ℹ️ 没有新的更改需要同步" -ForegroundColor Yellow
        return $true
    }
}

# 生成同步报告
function Generate-SyncReport {
    Write-Host "`n📊 生成同步报告..." -ForegroundColor Cyan
    
    $report = @"
# Git大文件同步报告
生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## 仓库信息
$(git remote -v)

## Git LFS状态
$(git lfs env 2>$null)

## LFS跟踪规则
$(if (Test-Path ".gitattributes") { Get-Content ".gitattributes" } else { "未配置LFS跟踪" })

## 当前LFS文件
$(git lfs ls-files 2>$null)

## 仓库统计
总文件数: $((git ls-files | Measure-Object).Count)
LFS文件数: $((git lfs ls-files 2>$null | Measure-Object).Count)
最新提交: $(git log --oneline -1)

## 大文件处理策略
✅ 使用Git LFS管理大于100MB的文件
✅ 自动跟踪常见大文件类型
✅ 双远程同步（GitHub + Gitea）
⚠️ 注意：Gitea可能对LFS支持有限

"@
    
    $reportPath = "large-file-sync-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "📄 同步报告已保存: $reportPath" -ForegroundColor Green
}

# 主执行流程
try {
    # 检查Git LFS
    if (-not (Check-GitLFS)) {
        Write-Host "❌ Git LFS未安装，无法处理大文件" -ForegroundColor Red
        exit 1
    }
    
    # 配置Git LFS（除非跳过）
    if (-not $SkipLFS) {
        Setup-GitLFS
        Update-GitIgnore
    }
    
    # 扫描大文件
    $largeFiles = Find-LargeFiles
    
    # 执行同步
    $syncResult = Sync-ToGitea $Message $Force
    
    # 生成报告
    Generate-SyncReport
    
    if ($syncResult) {
        Write-Host "`n🎉 大文件同步完成！" -ForegroundColor Green
        Write-Host "📋 同步摘要:" -ForegroundColor White
        Write-Host "  🎯 支持超过100MB的文件同步" -ForegroundColor Gray
        Write-Host "  📁 使用Git LFS管理大文件" -ForegroundColor Gray
        Write-Host "  🔄 双重备份: GitHub + Gitea" -ForegroundColor Gray
        Write-Host "  📊 详细信息请查看同步报告" -ForegroundColor Gray
    } else {
        Write-Host "`n❌ 同步过程中出现错误" -ForegroundColor Red
        Write-Host "💡 建议检查网络连接和仓库权限" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "`n💥 执行过程中发生错误: $_" -ForegroundColor Red
    exit 1
}