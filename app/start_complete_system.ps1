#requires -Version 5.1
param()

$ErrorActionPreference = 'SilentlyContinue'

function Get-PidsOnPort {
    param([int]$Port)
    $pids = @()
    try {
        $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
        $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    } catch {
        # Fallback to netstat parsing
        $lines = netstat -ano | Select-String ":$Port" | ForEach-Object { $_.ToString() }
        foreach ($line in $lines) {
            $tokens = $line -split '\s+'
            if ($tokens.Length -ge 5) { $pids += [int]$tokens[-1] }
        }
        $pids = $pids | Select-Object -Unique
    }
    return $pids
}

function Stop-Port {
    param([int]$Port)
    $pids = Get-PidsOnPort -Port $Port
    foreach ($pid in $pids) {
        try { Stop-Process -Id $pid -Force -ErrorAction Stop } catch {}
    }
}

Write-Host "🚀 启动课程管理系统 (Windows) ..." -ForegroundColor Cyan

# 计算脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1) 启动数据服务 (8080)
Write-Host "📊 启动数据服务 (8080) ..."
Stop-Port -Port 8080
$publicDir = Join-Path $ScriptDir 'frontend\public'
$pythonCmd = if (Get-Command py -ErrorAction SilentlyContinue) { 'py -3 -m http.server 8080' } else { 'python -m http.server 8080' }
$dataProc = Start-Process -FilePath powershell -ArgumentList @('-NoProfile','-NoLogo','-Command', $pythonCmd) -WorkingDirectory $publicDir -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 3

# 验证数据服务
try {
    Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:8080/data/schedules.json' -TimeoutSec 5 | Out-Null
    Write-Host "✅ 数据服务正常运行" -ForegroundColor Green
} catch {
    Write-Host "⚠️  数据服务检测失败，稍后前端可能无法读取演示数据" -ForegroundColor Yellow
}

# 2) 启动前端开发服务器 (3001)
Write-Host "🌐 启动前端开发服务器 (3001) ..."
Stop-Port -Port 3001
$frontendDir = Join-Path $ScriptDir 'frontend'
$env:VITE_USE_MOCK_API = 'true'
$env:VITE_DATA_SERVER_URL = 'http://localhost:8080'
$frontProc = Start-Process -FilePath npm -ArgumentList @('run','dev','--','--host','0.0.0.0','--port','3001') -WorkingDirectory $frontendDir -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 5

# 验证前端
try {
    Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:3001' -TimeoutSec 5 | Out-Null
    Write-Host "✅ 前端服务正常运行" -ForegroundColor Green
} catch {
    Write-Host "⚠️  前端服务可能需要更多时间启动 (http://localhost:3001)" -ForegroundColor Yellow
}

# 3) 保存 PID
$pidDataFile = Join-Path $env:TEMP 'schedule_data.pid'
$pidFrontFile = Join-Path $env:TEMP 'schedule_frontend.pid'
Set-Content -Path $pidDataFile -Value $dataProc.Id -Encoding ASCII
Set-Content -Path $pidFrontFile -Value $frontProc.Id -Encoding ASCII

Write-Host ""; Write-Host "🎉 系统启动完成！" -ForegroundColor Cyan
Write-Host ""; Write-Host "📋 访问地址:" -ForegroundColor White
Write-Host "   • 课程表查看: http://localhost:3001/#/schedules/view"
Write-Host "   • 排课管理:   http://localhost:3001/#/schedules/manage"
Write-Host "   • 冲突检测:   http://localhost:3001/#/schedules/conflicts"
Write-Host "   • 数据测试:   http://localhost:8080/data/schedules.json"
Write-Host ""
Write-Host "🔧 管理命令:" -ForegroundColor White
Write-Host "   • 停止数据服务:   Stop-Process -Id (Get-Content $pidDataFile) -Force"
Write-Host "   • 停止前端服务:   Stop-Process -Id (Get-Content $pidFrontFile) -Force"
Write-Host "   • 查看日志(当前会话):   Get-Content $pidDataFile, $pidFrontFile"
