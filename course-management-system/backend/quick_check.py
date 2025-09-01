import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

print(f'当前用户数: {User.objects.count()}')
print(f'百万级用户数: {User.objects.filter(username__startswith="million_").count()}')