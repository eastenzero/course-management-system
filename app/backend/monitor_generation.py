#!/usr/bin/env python
"""
简单的数据生成进度监控
"""
import os
import time
import django

# Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment

User = get_user_model()

def check_progress():
    """检查数据生成进度"""
    print(f"⏰ {time.strftime('%H:%M:%S')} 数据状态检查")
    print("-" * 50)
    
    # 检查用户数量
    total_users = User.objects.count()
    million_users = User.objects.filter(username__startswith='million_').count()
    
    # 检查课程数量
    total_courses = Course.objects.count()
    million_courses = Course.objects.filter(code__startswith='MILLION_').count()
    
    # 检查选课记录
    total_enrollments = Enrollment.objects.count()
    
    print(f"👥 总用户数: {total_users:,}")
    print(f"   百万级用户: {million_users:,}")
    print(f"📚 总课程数: {total_courses:,}")
    print(f"   百万级课程: {million_courses:,}")
    print(f"📝 选课记录: {total_enrollments:,}")
    
    grand_total = total_users + total_courses + total_enrollments
    print(f"🎯 总记录数: {grand_total:,}")
    
    if grand_total >= 1000000:
        print("✅ 已达到百万级数据目标！")
        return True
    else:
        progress = (grand_total / 1000000) * 100
        print(f"📊 完成进度: {progress:.1f}%")
        return False

if __name__ == '__main__':
    while True:
        try:
            completed = check_progress()
            if completed:
                print("🎉 数据生成完成！")
                break
            print()
            time.sleep(30)  # 每30秒检查一次
        except KeyboardInterrupt:
            print("\n监控已停止")
            break
        except Exception as e:
            print(f"❌ 检查出错: {e}")
            time.sleep(5)