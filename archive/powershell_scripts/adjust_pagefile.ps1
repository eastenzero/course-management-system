# 调整虚拟内存到G盘的PowerShell脚本
# 需要以管理员权限运行

Write-Host "正在调整虚拟内存设置到G盘..." -ForegroundColor Green

try {
    # 禁用自动管理虚拟内存
    $cs = Get-WmiObject -Class Win32_ComputerSystem -EnableAllPrivileges
    $cs.AutomaticManagedPagefile = $false
    $cs.Put()
    Write-Host "已禁用自动管理虚拟内存" -ForegroundColor Yellow

    # 删除现有的虚拟内存文件设置
    Get-WmiObject -Class Win32_PageFileSetting | ForEach-Object { 
        Write-Host "删除现有虚拟内存设置: $($_.Name)" -ForegroundColor Yellow
        $_.Delete() 
    }

    # 在G盘创建新的虚拟内存设置
    $pageFile = ([WMIClass]"Win32_PageFileSetting").CreateInstance()
    $pageFile.Name = "G:\pagefile.sys"
    $pageFile.InitialSize = 16384  # 16GB 初始大小
    $pageFile.MaximumSize = 32768  # 32GB 最大大小
    $pageFile.Put()
    
    Write-Host "已在G盘创建新的虚拟内存设置" -ForegroundColor Green
    Write-Host "初始大小: 16GB" -ForegroundColor Cyan
    Write-Host "最大大小: 32GB" -ForegroundColor Cyan
    
    Write-Host "" -ForegroundColor White
    Write-Host "设置完成！需要重启计算机才能生效。" -ForegroundColor Red
    Write-Host "重启后，虚拟内存将使用G盘，这应该能解决Git操作时的硬盘读写问题。" -ForegroundColor Green
    
} catch {
    Write-Host "错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请确保以管理员权限运行此脚本" -ForegroundColor Yellow
}

# 显示当前虚拟内存设置
Write-Host "" -ForegroundColor White
Write-Host "当前虚拟内存设置:" -ForegroundColor Cyan
Get-WmiObject -Class Win32_PageFile | Format-Table Name, Size, AllocatedBaseSize -AutoSize