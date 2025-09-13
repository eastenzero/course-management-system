from django.contrib.auth import get_user_model

User = get_user_model()

print("查看所有用户的用户类型：")
for user in User.objects.all():
    print(f"用户名: {user.username}, 用户类型: {user.user_type}, 显示名: {getattr(user, 'user_type_display', 'N/A')}")

print("\n查找admin用户：")
try:
    admin = User.objects.get(username='admin')
    print(f"Admin用户类型: {admin.user_type}")
    print(f"是否为超级用户: {admin.is_superuser}")
    print(f"是否为员工: {admin.is_staff}")
except User.DoesNotExist:
    print("未找到admin用户")