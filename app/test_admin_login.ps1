$response = Invoke-WebRequest -Uri 'http://localhost:18000/api/v1/auth/login/' -Method Post -Headers @{'Content-Type'='application/json'} -InFile 'g:\eaten\qoder\0814\course-management-system\test_login.json'
Write-Host "Login Response:"
$response.Content