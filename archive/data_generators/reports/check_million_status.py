#!/usr/bin/env python
"""
检查数据库百万级数据状态
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
import django
django.setup()

from django.contrib.auth.models import User
from courses.models import Course, Teacher, Student

def main():
    print("🔍 检查数据库百万级数据状态")
    print("=" * 60)
    
    # 检查当前数据量
    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_teachers = Teacher.objects.count() 
    total_students = Student.objects.count()
    
    # 检查百万级专用数据
    million_users = User.objects.filter(username__startswith='million_').count()
    
    print(f"📊 数据库当前状态:")
    print(f"用户总数: {total_users:,}")
    print(f"课程总数: {total_courses:,}")
    print(f"教师总数: {total_teachers:,}")
    print(f"学生总数: {total_students:,}")
    print(f"总记录数: {total_users + total_courses + total_teachers + total_students:,}")
    print()
    print(f"百万级用户: {million_users:,}")
    print()
    
    if total_users >= 1000000:
        print("✅ 已达到百万级数据标准!")
    else:
        shortage = 1000000 - total_users
        print(f"⚠️  距离百万级目标还需: {shortage:,} 条用户记录")
        print(f"完成度: {(total_users/1000000)*100:.2f}%")
        
        if million_users == 0:
            print("💡 建议运行 ultra_simple_million.py 生成百万级数据")
        elif million_users > 0:
            print(f"已有 {million_users:,} 条百万级数据，继续增加中...")

if __name__ == '__main__':
    main()