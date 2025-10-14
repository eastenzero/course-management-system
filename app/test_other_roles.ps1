# 测试教师登录
Write-Host "=== 测试教师登录 ==="
$response = Invoke-WebRequest -Uri 'http://localhost:18000/api/v1/auth/login/' -Method Post -Headers @{'Content-Type'='application/json'} -InFile 'g:\\eaten\\qoder\\0814\\course-management-system\\test_teacher_login.json'
$content = $response.Content | ConvertFrom-Json
Write-Host "Teacher user_type: $($content.data.user.user_type)"
Write-Host ""

# 测试学生登录
Write-Host "=== 测试学生登录 ==="
$response = Invoke-WebRequest -Uri 'http://localhost:18000/api/v1/auth/login/' -Method Post -Headers @{'Content-Type'='application/json'} -InFile 'g:\\eaten\\qoder\\0814\\course-management-system\\test_student_login.json'
$content = $response.Content | ConvertFrom-Json
Write-Host "Student user_type: $($content.data.user.user_type)"