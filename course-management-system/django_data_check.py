#!/usr/bin/env python3
"""
通过Django Shell检查数据库数据的脚本
"""

# 导入Django模型
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Classroom
from apps.schedules.models import TimeSlot
from django.db.models import Count, Avg

# 获取用户模型
User = get_user_model()

print("=" * 80)
print("🏫 校园课程管理系统 - 数据验证报告")
print("=" * 80)

# 检查各表的数据量
tables_info = [
    (User, '用户总数'),
    (Course, '课程总数'), 
    (Enrollment, '选课记录总数'),
    (Classroom, '教室总数'),
    (TimeSlot, '时间段总数')
]

print("📊 数据表统计信息：")
print("=" * 60)

total_records = 0
for model, description in tables_info:
    try:
        count = model.objects.count()
        total_records += count
        print(f"  {description:<15}: {count:>10,}")
    except Exception as e:
        print(f"  {description:<15}: 查询失败 ({e})")

print("=" * 60)
print(f"  总记录数: {total_records:>20,}")

# 检查用户角色分布
print("\n👥 用户角色分布：")
print("=" * 40)
try:
    user_dist = User.objects.values('user_type').annotate(count=Count('id')).order_by('-count')
    for item in user_dist:
        user_type = item['user_type'] or '未设置'
        count = item['count']
        print(f"  {user_type:<15}: {count:>8,}")
except Exception as e:
    print(f"❌ 用户分布查询失败: {e}")

# 检查课程类型分布
print("\n📚 课程类型分布：")
print("=" * 40)
try:
    course_dist = Course.objects.values('course_type').annotate(count=Count('id')).order_by('-count')
    for item in course_dist:
        course_type = item['course_type'] or '未设置'
        count = item['count']
        print(f"  {course_type:<15}: {count:>8,}")
except Exception as e:
    print(f"❌ 课程分布查询失败: {e}")

# 检查选课统计
print("\n📝 选课统计信息：")
print("=" * 50)
try:
    total_students = Enrollment.objects.values('student').distinct().count()
    total_enrollments = Enrollment.objects.count()
    avg_courses = total_enrollments / total_students if total_students > 0 else 0
    
    print(f"  参与选课学生数: {total_students:>12,}")
    print(f"  总选课记录数: {total_enrollments:>14,}")
    print(f"  平均每人选课数: {avg_courses:>12.2f}")
except Exception as e:
    print(f"❌ 选课统计查询失败: {e}")

# 获取测试账号样本
print("\n🔑 测试账号样本：")
print("=" * 80)

user_types = ['admin', 'academic_admin', 'teacher', 'student']
for user_type in user_types:
    print(f"\n{user_type.upper()}角色账号:")
    try:
        samples = User.objects.filter(user_type=user_type)[:5]
        if samples:
            for user in samples:
                name = f"{user.first_name} {user.last_name}".strip() or "未设置"
                print(f"  • 用户名: {user.username:<15} 姓名: {name:<10} 邮箱: {user.email or '未设置'}")
        else:
            print("  无此角色用户")
    except Exception as e:
        print(f"  查询失败: {e}")

# 生成总结
print("\n" + "=" * 80)
print("📋 验证结果总结：")
print("=" * 80)

if total_records >= 400000:
    print(f"✅ 数据规模验证通过: {total_records:,} 条记录 (≥400K)")
else:
    print(f"❌ 数据规模不足: {total_records:,} 条记录 (<400K)")

if total_records >= 1000000:
    print("🎉 已达到百万级数据规模！")
elif total_records >= 400000:
    print("✅ 已达到大规模数据标准")
else:
    print("⚠️  数据规模偏小，建议检查数据导入")

print("\n💡 建议使用的测试账号（默认密码：password123）：")
print("-" * 60)

# 显示推荐测试账号
try:
    admin_users = User.objects.filter(user_type='admin')[:1]
    teacher_users = User.objects.filter(user_type='teacher')[:3]  
    student_users = User.objects.filter(user_type='student')[:3]
    
    if admin_users:
        admin = admin_users[0]
        print(f"  ADMIN   : {admin.username:<15} ({admin.first_name} {admin.last_name})")
    
    if teacher_users:
        for teacher in teacher_users:
            name = f"{teacher.first_name} {teacher.last_name}".strip() or "未设置"
            print(f"  TEACHER : {teacher.username:<15} ({name})")
    
    if student_users:
        for student in student_users:
            name = f"{student.first_name} {student.last_name}".strip() or "未设置"
            print(f"  STUDENT : {student.username:<15} ({name})")
            
except Exception as e:
    print(f"❌ 推荐账号查询失败: {e}")

print("\n" + "=" * 80)