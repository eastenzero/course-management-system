#!/usr/bin/env python
"""
百万级数据生成进度监控脚本
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
import time

User = get_user_model()

def monitor_progress():
    """监控数据生成进度"""
    while True:
        try:
            # 统计当前数据量
            total_users = User.objects.count()
            million_users = User.objects.filter(username__startswith='million_').count()
            million_students = User.objects.filter(username__startswith='million_student_').count()
            million_teachers = User.objects.filter(username__startswith='million_teacher_').count()
            
            total_courses = Course.objects.count()
            million_courses = Course.objects.filter(code__startswith='MILLION_').count()
            
            total_enrollments = Enrollment.objects.count()
            
            # 计算总记录数
            grand_total = total_users + total_courses + total_enrollments
            
            print(f"\n📊 数据生成进度监控 - {time.strftime('%H:%M:%S')}")
            print(f"=" * 60)
            print(f"👥 用户数据:")
            print(f"   总用户数: {total_users:,}")
            print(f"   百万级用户: {million_users:,}")
            print(f"   └─ 学生: {million_students:,}")
            print(f"   └─ 教师: {million_teachers:,}")
            
            print(f"\n📚 课程数据:")
            print(f"   总课程数: {total_courses:,}")
            print(f"   百万级课程: {million_courses:,}")
            
            print(f"\n📝 选课数据:")
            print(f"   总选课记录: {total_enrollments:,}")
            
            print(f"\n🎯 总体进度:")
            print(f"   数据库总记录: {grand_total:,}")
            progress = (grand_total / 1000000) * 100
            print(f"   百万级进度: {progress:.1f}%")
            
            if grand_total >= 1000000:
                print(f"✅ 已达到百万级数据标准！")
                break
            else:
                remaining = 1000000 - grand_total
                print(f"   还需生成: {remaining:,} 条记录")
            
            print(f"=" * 60)
            
            # 等待60秒再次检查
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n监控停止")
            break
        except Exception as e:
            print(f"监控错误: {e}")
            time.sleep(30)

if __name__ == '__main__':
    monitor_progress()