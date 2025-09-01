#!/usr/bin/env python
"""
创建默认管理员用户脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

def create_superuser():
    """创建默认超级用户"""
    username = 'admin'
    email = 'admin@course-management.com'
    password = 'admin123456'
    
    if User.objects.filter(username=username).exists():
        print(f"用户 '{username}' 已存在")
        user = User.objects.get(username=username)
        print(f"用户ID: {user.id}")
        print(f"邮箱: {user.email}")
        print(f"是否为超级用户: {user.is_superuser}")
        return user
    
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    print(f"✅ 超级用户创建成功!")
    print(f"用户名: {username}")
    print(f"邮箱: {email}")
    print(f"密码: {password}")
    print(f"用户ID: {user.id}")
    
    return user

if __name__ == '__main__':
    try:
        create_superuser()
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        sys.exit(1)