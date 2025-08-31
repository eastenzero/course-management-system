#!/usr/bin/env python3
"""
批量重置测试账号密码脚本
用于快速配置百万级数据中的测试账号
"""

import subprocess
import sys

def reset_password_via_docker(username, password="password123"):
    """通过Docker容器重置用户密码"""
    command = f'''docker exec course_management_backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    user = User.objects.get(username='{username}')
    user.set_password('{password}')
    user.save()
    print('✅ {username} 密码重置成功')
except User.DoesNotExist:
    print('❌ 用户 {username} 不存在')
except Exception as e:
    print('❌ {username} 密码重置失败: {{e}}')
"'''
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"❌ 命令执行失败: {result.stderr}")
    except Exception as e:
        print(f"❌ 执行异常: {e}")

def main():
    print("🔑 批量重置测试账号密码")
    print("=" * 50)
    
    # 推荐的教师测试账号
    teacher_accounts = [
        "teacher_T000001",
        "teacher_T000002", 
        "teacher_T000003",
        "teacher_T000004",
        "teacher_T000005",
        "teacher_T000010",
        "teacher_T000015",
        "teacher_T000020"
    ]
    
    # 推荐的学生测试账号
    student_accounts = [
        "student_20201330001",
        "student_20221530002",
        "student_20210930003", 
        "student_20240430004",
        "student_2024120001",
        "student_2023140002",
        "student_2022140003",
        "student_2020120004",
        "student_2022090005",
        "student_2023120006"
    ]
    
    print(f"👨‍🏫 重置教师账号密码 ({len(teacher_accounts)}个)")
    print("-" * 30)
    for username in teacher_accounts:
        reset_password_via_docker(username)
    
    print(f"\n🎓 重置学生账号密码 ({len(student_accounts)}个)")  
    print("-" * 30)
    for username in student_accounts:
        reset_password_via_docker(username)
    
    print(f"\n✅ 批量密码重置完成!")
    print(f"📋 默认密码: password123")
    print(f"🌐 登录地址: http://localhost:18081")
    print(f"👑 管理员: admin / admin123")

if __name__ == "__main__":
    main()