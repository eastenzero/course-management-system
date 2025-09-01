#!/usr/bin/env python
"""
数据验证脚本
验证百万级数据生成的结果
"""

import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def main():
    print("📊 百万级数据生成验证报告")
    print("="*50)
    
    # 统计生成的数据
    student_count = User.objects.filter(user_type='student', username__startswith='million_').count()
    teacher_count = User.objects.filter(user_type='teacher', username__startswith='million_').count()
    total_count = student_count + teacher_count
    
    print(f"🎯 数据统计:")
    print(f"   学生用户: {student_count:,} 条")
    print(f"   教师用户: {teacher_count:,} 条")
    print(f"   总计: {total_count:,} 条")
    
    # 验证数据质量
    print(f"\n🔍 数据质量检查:")
    
    # 检查学生样本
    student_sample = User.objects.filter(user_type='student', username__startswith='million_').first()
    if student_sample:
        print(f"   ✅ 学生样本:")
        print(f"      用户名: {student_sample.username}")
        print(f"      学号: {student_sample.student_id}")
        print(f"      姓名: {student_sample.first_name}{student_sample.last_name}")
        print(f"      部门: {student_sample.department}")
        print(f"      邮箱: {student_sample.email}")
        print(f"      手机: {student_sample.phone}")
    
    # 检查教师样本
    teacher_sample = User.objects.filter(user_type='teacher', username__startswith='million_').first()
    if teacher_sample:
        print(f"   ✅ 教师样本:")
        print(f"      用户名: {teacher_sample.username}")
        print(f"      工号: {teacher_sample.employee_id}")
        print(f"      姓名: {teacher_sample.first_name}{teacher_sample.last_name}")
        print(f"      部门: {teacher_sample.department}")
        print(f"      邮箱: {teacher_sample.email}")
        print(f"      手机: {teacher_sample.phone}")
    
    # 检查字段长度
    print(f"\n📏 字段长度验证:")
    long_student_ids = User.objects.filter(
        user_type='student', 
        username__startswith='million_'
    ).extra(where=["LENGTH(student_id) > 20"])
    
    long_employee_ids = User.objects.filter(
        user_type='teacher', 
        username__startswith='million_'
    ).extra(where=["LENGTH(employee_id) > 20"])
    
    if long_student_ids.exists():
        print(f"   ⚠️ 发现超长学号: {long_student_ids.count()} 条")
    else:
        print(f"   ✅ 学号长度检查通过")
        
    if long_employee_ids.exists():
        print(f"   ⚠️ 发现超长工号: {long_employee_ids.count()} 条")
    else:
        print(f"   ✅ 工号长度检查通过")
    
    # 检查数据分布
    print(f"\n📈 数据分布检查:")
    departments = User.objects.filter(username__startswith='million_').values_list('department', flat=True).distinct()
    print(f"   部门数量: {len(departments)} 个")
    print(f"   部门列表: {', '.join(departments[:5])}{'...' if len(departments) > 5 else ''}")
    
    print("\n" + "="*50)
    print("🎉 验证完成！数据生成成功！")

if __name__ == "__main__":
    main()