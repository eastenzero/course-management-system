# 虚拟内存调整完成 - 重启后验证脚本

Write-Host "=== 虚拟内存调整状态检查 ===" -ForegroundColor Green

# 检查当前虚拟内存设置
Write-Host "`n1. 检查虚拟内存配置:" -ForegroundColor Cyan
Get-WmiObject -Class Win32_PageFileSetting | Format-Table Name, InitialSize, MaximumSize -AutoSize

# 检查实际的虚拟内存文件
Write-Host "`n2. 检查实际虚拟内存文件:" -ForegroundColor Cyan
$pageFiles = @("C:\pagefile.sys", "D:\pagefile.sys", "G:\pagefile.sys")
foreach ($file in $pageFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length / 1MB
        Write-Host "✓ $file 存在 (大小: $([math]::Round($size, 2)) MB)" -ForegroundColor Green
    } else {
        Write-Host "✗ $file 不存在" -ForegroundColor Gray
    }
}

# 检查自动管理状态
Write-Host "`n3. 检查自动管理状态:" -ForegroundColor Cyan
$autoManaged = (Get-WmiObject -Class Win32_ComputerSystem).AutomaticManagedPagefile
Write-Host "自动管理虚拟内存: $autoManaged" -ForegroundColor $(if($autoManaged) {"Yellow"} else {"Green"})

# 显示磁盘空间
Write-Host "`n4. 检查G盘空间:" -ForegroundColor Cyan
Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "G:"} | ForEach-Object {
    $freeGB = [math]::Round($_.FreeSpace / 1GB, 2)
    $totalGB = [math]::Round($_.Size / 1GB, 2)
    Write-Host "G盘可用空间: $freeGB GB / $totalGB GB" -ForegroundColor Green
}

Write-Host "`n=== 下一步操作 ===" -ForegroundColor Yellow
Write-Host "1. 保存所有工作" -ForegroundColor White
Write-Host "2. 重启计算机" -ForegroundColor White  
Write-Host "3. 重启后运行此脚本验证设置" -ForegroundColor White
Write-Host "4. 测试Git操作，观察D盘读写情况" -ForegroundColor White

Write-Host "`n是否现在重启计算机? (Y/N): " -ForegroundColor Red -NoNewline
$response = Read-Host
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "正在重启计算机..." -ForegroundColor Yellow
    Restart-Computer -Force
}