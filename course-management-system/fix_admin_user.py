from django.contrib.auth import get_user_model

User = get_user_model()

print("修正admin用户类型...")

# 修正admin用户的user_type
admin = User.objects.get(username='admin')
admin.user_type = 'admin'
admin.save()

print(f"Admin用户类型已修正: {admin.user_type}")

# 也检查是否有其他需要修正的管理员账号
for user in User.objects.filter(is_superuser=True):
    if user.user_type != 'admin':
        print(f"发现超级用户 {user.username} 的用户类型为 {user.user_type}，修正为 admin")
        user.user_type = 'admin'
        user.save()
    
print("所有管理员用户类型已修正完成")