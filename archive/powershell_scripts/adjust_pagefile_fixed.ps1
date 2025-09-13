# 虚拟内存调整到G盘 - 修复版本
Write-Host "开始调整虚拟内存到G盘..." -ForegroundColor Green

try {
    # 删除现有的D盘虚拟内存设置
    $existingPageFile = Get-WmiObject -Class Win32_PageFileSetting | Where-Object {$_.Name -like "D:*"}
    if ($existingPageFile) {
        Write-Host "删除D盘上的虚拟内存设置..." -ForegroundColor Yellow
        $existingPageFile.Delete()
    }
    
    # 创建G盘虚拟内存设置
    Write-Host "在G盘创建虚拟内存..." -ForegroundColor Yellow
    $newPageFile = ([WMIClass]"Win32_PageFileSetting").CreateInstance()
    $newPageFile.Name = "G:\pagefile.sys"
    $newPageFile.InitialSize = 16384
    $newPageFile.MaximumSize = 32768
    $result = $newPageFile.Put()
    
    if ($result.ReturnValue -eq 0) {
        Write-Host "成功在G盘创建虚拟内存设置!" -ForegroundColor Green
        Write-Host "初始大小: 16GB, 最大大小: 32GB" -ForegroundColor Cyan
    } else {
        Write-Host "创建虚拟内存设置时出现错误: $($result.ReturnValue)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "执行过程中发生错误: $($_.Exception.Message)" -ForegroundColor Red
}

# 显示新的设置
Write-Host "`n当前虚拟内存设置:" -ForegroundColor Cyan
Get-WmiObject -Class Win32_PageFileSetting | Format-Table Name, InitialSize, MaximumSize -AutoSize

Write-Host "`n重要提示: 需要重启计算机才能使新设置生效!" -ForegroundColor Red -BackgroundColor Yellow