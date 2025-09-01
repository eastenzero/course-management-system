#!/usr/bin/env python
"""
修复版百万级数据生成器 - 确保字段长度符合数据库约束
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.contrib.auth.hashers import make_password
from apps.courses.models import Course, Enrollment
import time
import random
from datetime import datetime, timedelta

User = get_user_model()

# 预计算密码哈希
STUDENT_PASSWORD = make_password('student123')
TEACHER_PASSWORD = make_password('teacher123')

# 预定义数据
DEPARTMENTS = ['计算机学院', '软件学院', '信息学院', '人工智能学院', '网络安全学院']
SUBJECTS = ['高等数学', '线性代数', '概率论', '数据结构', '算法设计', '计算机网络', '数据库原理', '软件工程']
SURNAMES = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴']
GIVEN_NAMES = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋']

def generate_name():
    """生成简短中文姓名"""
    return random.choice(SURNAMES) + random.choice(GIVEN_NAMES)

def generate_phone():
    """生成手机号"""
    return f"1{random.randint(30, 89):02d}{random.randint(1000000, 9999999)}"

def stage1_generate_students():
    """阶段1：生成80万学生"""
    print("\n🎯 阶段1：生成 800,000 名学生用户")
    print("=" * 60)
    
    BATCH_SIZE = 5000  # 减少批次大小
    TARGET = 800000
    created = 0
    start_time = time.time()
    
    # 清理现有百万级数据
    User.objects.filter(username__startswith='million_').delete()
    Course.objects.filter(code__startswith='MILLION_').delete()
    
    for batch_start in range(0, TARGET, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, TARGET)
        users = []
        
        for i in range(batch_start, batch_end):
            student_num = i + 1
            name = generate_name()
            
            # 确保字段长度不超过限制
            username = f"million_s_{student_num:07d}"  # 缩短用户名
            email = f"s{student_num:07d}@univ.edu"  # 缩短邮箱
            
            users.append(User(
                username=username[:20],  # 限制长度
                email=email[:50],  # 限制长度
                first_name=name[:1][:30],  # 姓
                last_name=name[1:][:30] if len(name) > 1 else '',  # 名
                user_type='student',
                department=random.choice(DEPARTMENTS)[:50],  # 限制长度
                student_id=f"S{student_num:07d}"[:20],  # 限制长度
                phone=generate_phone()[:20],  # 限制长度
                password=STUDENT_PASSWORD,
                is_active=True
            ))
        
        try:
            with transaction.atomic():
                User.objects.bulk_create(users, ignore_conflicts=True)
                created += len(users)
        except Exception as e:
            print(f"   批次错误: {e}")
            continue
        
        if batch_start % 50000 == 0:
            elapsed = time.time() - start_time
            speed = created / elapsed if elapsed > 0 else 0
            progress = (created / TARGET) * 100
            print(f"   学生进度: {created:,}/{TARGET:,} ({progress:.1f}%) | 速度: {speed:.0f} 条/秒")
    
    elapsed = time.time() - start_time
    print(f"✅ 阶段1完成: {created:,} 学生用户，耗时 {elapsed:.1f} 秒")
    return created

def stage2_generate_teachers():
    """阶段2：生成5万教师"""
    print("\n🎯 阶段2：生成 50,000 名教师用户")
    print("=" * 60)
    
    BATCH_SIZE = 2000
    TARGET = 50000
    created = 0
    start_time = time.time()
    
    for batch_start in range(0, TARGET, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, TARGET)
        users = []
        
        for i in range(batch_start, batch_end):
            teacher_num = i + 1
            name = generate_name()
            
            username = f"million_t_{teacher_num:05d}"
            email = f"t{teacher_num:05d}@univ.edu"
            
            users.append(User(
                username=username[:20],
                email=email[:50],
                first_name=name[:1][:30],
                last_name=name[1:][:30] if len(name) > 1 else '',
                user_type='teacher',
                department=random.choice(DEPARTMENTS)[:50],
                employee_id=f"T{teacher_num:05d}"[:20],
                phone=generate_phone()[:20],
                password=TEACHER_PASSWORD,
                is_active=True
            ))
        
        try:
            with transaction.atomic():
                User.objects.bulk_create(users, ignore_conflicts=True)
                created += len(users)
        except Exception as e:
            print(f"   教师批次错误: {e}")
            continue
        
        if batch_start % 20000 == 0:
            progress = (created / TARGET) * 100
            print(f"   教师进度: {created:,}/{TARGET:,} ({progress:.1f}%)")
    
    elapsed = time.time() - start_time
    print(f"✅ 阶段2完成: {created:,} 教师用户，耗时 {elapsed:.1f} 秒")
    return created

def stage3_generate_courses():
    """阶段3：生成5万课程"""
    print("\n🎯 阶段3：生成 50,000 门课程")
    print("=" * 60)
    
    # 获取部分教师ID
    teachers = list(User.objects.filter(user_type='teacher').values_list('id', flat=True)[:10000])
    if not teachers:
        print("没有教师用户，跳过课程生成")
        return 0
    
    BATCH_SIZE = 2000
    TARGET = 50000
    created = 0
    start_time = time.time()
    
    for batch_start in range(0, TARGET, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, TARGET)
        courses = []
        
        for i in range(batch_start, batch_end):
            course_num = i + 1
            subject = random.choice(SUBJECTS)
            level = random.choice(['基础', '进阶', '高级'])
            
            courses.append(Course(
                code=f"MILLION_{course_num:05d}"[:20],  # 限制长度
                name=f"{subject}({level})"[:100],  # 限制长度
                description=f"{subject}课程"[:500],  # 限制长度
                credits=random.choice([2, 3, 4]),
                max_capacity=random.randint(30, 150),
                instructor_id=random.choice(teachers),
                department=random.choice(DEPARTMENTS)[:50],
                semester='2024秋季'[:20],
                academic_year='2024-2025'[:20],
                is_active=True
            ))
        
        try:
            with transaction.atomic():
                Course.objects.bulk_create(courses, ignore_conflicts=True)
                created += len(courses)
        except Exception as e:
            print(f"   课程批次错误: {e}")
            continue
        
        if batch_start % 20000 == 0:
            progress = (created / TARGET) * 100
            print(f"   课程进度: {created:,}/{TARGET:,} ({progress:.1f}%)")
    
    elapsed = time.time() - start_time
    print(f"✅ 阶段3完成: {created:,} 课程，耗时 {elapsed:.1f} 秒")
    return created

def stage4_generate_enrollments():
    """阶段4：生成20万选课记录"""
    print("\n🎯 阶段4：生成 200,000 条选课记录")
    print("=" * 60)
    
    # 获取部分学生和课程ID
    students = list(User.objects.filter(user_type='student', username__startswith='million_').values_list('id', flat=True)[:50000])
    courses = list(Course.objects.filter(code__startswith='MILLION_').values_list('id', flat=True))
    
    if not students or not courses:
        print("缺少学生或课程数据，跳过选课记录生成")
        return 0
    
    BATCH_SIZE = 5000
    TARGET = 200000
    created = 0
    start_time = time.time()
    
    for batch_start in range(0, TARGET, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, TARGET)
        enrollments = []
        
        for i in range(batch_start, batch_end):
            enrollments.append(Enrollment(
                student_id=random.choice(students),
                course_id=random.choice(courses),
                enrollment_date=datetime.now() - timedelta(days=random.randint(0, 180)),
                status=random.choice(['enrolled', 'completed'])[:20],  # 限制长度
                grade=random.choice(['A', 'B', 'C']) if random.random() > 0.3 else None
            ))
        
        try:
            with transaction.atomic():
                Enrollment.objects.bulk_create(enrollments, ignore_conflicts=True)
                created += len(enrollments)
        except Exception as e:
            print(f"   选课批次错误: {e}")
            continue
        
        if batch_start % 50000 == 0:
            progress = (created / TARGET) * 100
            print(f"   选课进度: {created:,}/{TARGET:,} ({progress:.1f}%)")
    
    elapsed = time.time() - start_time
    print(f"✅ 阶段4完成: {created:,} 选课记录，耗时 {elapsed:.1f} 秒")
    return created

def main():
    """主函数"""
    print("🚀 修复版百万级数据生成系统启动")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("目标: 生成超过 1,100,000 条记录")
    print("=" * 80)
    
    total_start = time.time()
    
    # 分阶段执行
    students = stage1_generate_students()
    teachers = stage2_generate_teachers()
    courses = stage3_generate_courses()
    enrollments = stage4_generate_enrollments()
    
    total_created = students + teachers + courses + enrollments
    total_elapsed = time.time() - total_start
    
    print("\n" + "=" * 80)
    print("🎉 百万级数据生成完成！")
    print("=" * 80)
    print(f"生成统计:")
    print(f"  学生用户: {students:,}")
    print(f"  教师用户: {teachers:,}")
    print(f"  课程数据: {courses:,}")
    print(f"  选课记录: {enrollments:,}")
    print(f"  总记录数: {total_created:,}")
    print(f"总耗时: {total_elapsed/60:.1f} 分钟")
    print(f"平均速度: {total_created/total_elapsed:.0f} 条/秒")
    
    # 最终验证
    print("\n🔍 最终验证:")
    final_users = User.objects.count()
    final_courses = Course.objects.count()
    final_enrollments = Enrollment.objects.count()
    grand_total = final_users + final_courses + final_enrollments
    
    print(f"  数据库总用户: {final_users:,}")
    print(f"  数据库总课程: {final_courses:,}")
    print(f"  数据库总选课: {final_enrollments:,}")
    print(f"  数据库总记录: {grand_total:,}")
    
    if grand_total >= 1000000:
        print(f"✅ 成功达到百万级数据标准！超出目标 {grand_total - 1000000:,} 条记录")
    else:
        print(f"❌ 未达到百万级标准，还差 {1000000 - grand_total:,} 条记录")
    
    print("=" * 80)

if __name__ == '__main__':
    main()