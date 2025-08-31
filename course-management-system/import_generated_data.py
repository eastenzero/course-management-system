#!/usr/bin/env python
"""
导入生成的测试数据到Django数据库
将data-generator生成的数据适配到Django模型并导入
"""

import os
import sys
import json
import django
from datetime import datetime, date
from decimal import Decimal
import random

# 设置Django环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.courses.models import Course, Enrollment

User = get_user_model()

def load_generated_data():
    """加载生成的JSON数据"""
    data_file = '/app/course_data.json'
    
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        return None
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ 成功加载数据文件: {data_file}")
    print(f"📊 数据规模: 总计 {data['metadata']['total_records']:,} 条记录")
    return data

def create_departments(departments_data):
    """创建院系数据（作为用户的department字段）"""
    print("\n📚 处理院系数据...")
    
    # 提取院系名称供后续使用
    dept_names = [dept['name'] for dept in departments_data]
    print(f"   ✅ 处理 {len(dept_names)} 个院系名称")
    return dept_names

def create_students(students_data, majors_data, dept_names):
    """创建学生用户和档案"""
    print(f"\n👥 创建学生用户...")
    
    # 创建专业名称映射
    major_map = {major['id']: major['name'] for major in majors_data}
    
    created_count = 0
    updated_count = 0
    
    # 预计算密码哈希以提高性能
    from django.contrib.auth.hashers import make_password
    default_password_hash = make_password('student123')

    total_students = len(students_data)
    print(f"   📊 计划创建 {total_students} 个学生用户...")

    for i, student_data in enumerate(students_data):  # 导入全部学生
        try:
            # 显示进度
            if (i + 1) % 500 == 0:
                print(f"   📈 进度: {i + 1}/{total_students} ({((i + 1)/total_students*100):.1f}%)")

            # 准备用户数据
            username = f"student_{student_data['student_id']}"

            # 检查用户是否已存在
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{username}@university.edu.cn",
                    'first_name': student_data['name'].split()[0] if student_data['name'] else '学生',
                    'last_name': student_data['name'].split()[-1] if len(student_data['name'].split()) > 1 else '',
                    'user_type': 'student',
                    'student_id': student_data['student_id'],
                    'department': random.choice(dept_names) if dept_names else '未分配',
                    'phone': student_data.get('phone', ''),
                    'is_active': student_data.get('is_active', True),
                    'password': default_password_hash,  # 使用预计算的密码哈希
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1
            
            # 创建学生档案
            major_name = major_map.get(student_data.get('major_id'), '未分配专业')
            
            profile, profile_created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'admission_year': student_data.get('grade', 2024),
                    'major': major_name,
                    'class_name': f"{major_name}{student_data.get('class_number', 1)}班",
                    'gpa': Decimal(str(student_data.get('gpa', 0.0))),
                    'total_credits': student_data.get('total_credits', 0),
                    'completed_credits': student_data.get('completed_credits', 0),
                    'enrollment_status': 'active',
                }
            )
            
        except Exception as e:
            print(f"   ⚠️  创建学生 {student_data.get('name', 'Unknown')} 时出错: {e}")
            continue
    
    print(f"   ✅ 创建 {created_count} 个新学生用户")
    print(f"   ✅ 更新 {updated_count} 个已存在学生用户")
    return created_count + updated_count

def create_teachers(teachers_data, dept_names):
    """创建教师用户和档案"""
    print(f"\n👨‍🏫 创建教师用户...")
    
    created_count = 0
    updated_count = 0
    
    # 预计算密码哈希以提高性能
    from django.contrib.auth.hashers import make_password
    teacher_password_hash = make_password('teacher123')

    total_teachers = len(teachers_data)
    print(f"   📊 计划创建 {total_teachers} 个教师用户...")

    for i, teacher_data in enumerate(teachers_data):  # 导入全部教师
        try:
            # 显示进度
            if (i + 1) % 100 == 0:
                print(f"   📈 进度: {i + 1}/{total_teachers} ({((i + 1)/total_teachers*100):.1f}%)")

            # 准备用户数据
            username = f"teacher_{teacher_data['employee_id']}"

            # 检查用户是否已存在
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{username}@university.edu.cn",
                    'first_name': teacher_data['name'].split()[0] if teacher_data['name'] else '教师',
                    'last_name': teacher_data['name'].split()[-1] if len(teacher_data['name'].split()) > 1 else '',
                    'user_type': 'teacher',
                    'employee_id': teacher_data['employee_id'],
                    'department': random.choice(dept_names) if dept_names else '未分配',
                    'phone': teacher_data.get('phone', ''),
                    'is_active': teacher_data.get('is_active', True),
                    'password': teacher_password_hash,  # 使用预计算的密码哈希
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1
            
            # 创建教师档案
            profile, profile_created = TeacherProfile.objects.get_or_create(
                user=user,
                defaults={
                    'title': random.choice(['assistant', 'lecturer', 'associate_professor', 'professor']),
                    'research_area': f"{user.department}相关研究",
                    'office_location': f"{user.department}大楼{random.randint(100, 999)}室",
                    'teaching_experience': random.randint(1, 20),
                    'education_background': '博士研究生',
                    'is_active_teacher': True,
                }
            )
            
        except Exception as e:
            print(f"   ⚠️  创建教师 {teacher_data.get('name', 'Unknown')} 时出错: {e}")
            continue
    
    print(f"   ✅ 创建 {created_count} 个新教师用户")
    print(f"   ✅ 更新 {updated_count} 个已存在教师用户")
    return created_count + updated_count

def create_courses(courses_data, dept_names):
    """创建课程"""
    print(f"\n📖 创建课程...")
    
    created_count = 0
    updated_count = 0
    
    # 获取可用的教师
    teachers = list(User.objects.filter(user_type='teacher')[:100])
    
    total_courses = len(courses_data)
    print(f"   📊 计划创建 {total_courses} 门课程...")

    for i, course_data in enumerate(courses_data):  # 导入全部课程
        try:
            # 显示进度
            if (i + 1) % 200 == 0:
                print(f"   📈 进度: {i + 1}/{total_courses} ({((i + 1)/total_courses*100):.1f}%)")
            # 映射课程类型
            course_type_map = {
                '必修': 'required',
                '选修': 'elective',
                '限选': 'elective',
                '通识': 'public'
            }
            
            course_type = course_type_map.get(course_data.get('type', '选修'), 'elective')
            
            # 检查课程是否已存在
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    'name': course_data['name'],
                    'english_name': course_data.get('english_name', ''),
                    'course_type': course_type,
                    'credits': course_data.get('credits', 3),
                    'hours': course_data.get('hours', 48),
                    'department': random.choice(dept_names) if dept_names else '通用',
                    'semester': course_data.get('semester', '2024-2025-1'),
                    'academic_year': '2024-2025',
                    'description': course_data.get('description', ''),
                    'max_students': random.randint(30, 120),
                    'min_students': random.randint(10, 30),
                }
            )
            
            if created:
                # 为课程分配教师
                if teachers:
                    selected_teachers = random.sample(teachers, min(random.randint(1, 2), len(teachers)))
                    course.teachers.set(selected_teachers)
                created_count += 1
            else:
                updated_count += 1
                
        except Exception as e:
            print(f"   ⚠️  创建课程 {course_data.get('name', 'Unknown')} 时出错: {e}")
            continue
    
    print(f"   ✅ 创建 {created_count} 门新课程")
    print(f"   ✅ 更新 {updated_count} 门已存在课程")
    return created_count + updated_count

def create_enrollments(enrollments_data):
    """创建选课记录"""
    print(f"\n📝 创建选课记录...")
    
    created_count = 0
    
    # 获取现有的学生和课程
    students = list(User.objects.filter(user_type='student'))
    courses = list(Course.objects.all())
    
    if not students or not courses:
        print("   ⚠️  没有找到学生或课程，跳过选课记录创建")
        return 0
    
    # 为每个学生随机分配一些课程
    for student in students:  # 为所有学生创建选课记录
        try:
            # 每个学生选择3-8门课程
            num_courses = random.randint(3, 8)
            selected_courses = random.sample(courses, min(num_courses, len(courses)))
            
            for course in selected_courses:
                # 检查是否已经选过这门课
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'status': 'enrolled',
                        'score': None,  # 初始没有成绩
                        'grade': '',
                    }
                )
                
                if created:
                    created_count += 1
                    
        except Exception as e:
            print(f"   ⚠️  为学生 {student.username} 创建选课记录时出错: {e}")
            continue
    
    print(f"   ✅ 创建 {created_count} 条选课记录")
    return created_count

def create_test_accounts():
    """创建特定的测试账号"""
    print("\n🔑 创建特定测试账号...")
    
    test_accounts = []
    
    # 创建管理员账号
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@university.edu.cn',
            'first_name': '系统',
            'last_name': '管理员',
            'user_type': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'department': '系统管理部',
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        test_accounts.append(('admin', 'admin123', '系统管理员'))
    
    # 创建测试教师账号
    teacher_user, created = User.objects.get_or_create(
        username='test_teacher',
        defaults={
            'email': 'teacher@university.edu.cn',
            'first_name': '张',
            'last_name': '教授',
            'user_type': 'teacher',
            'employee_id': 'T001001',
            'department': '计算机科学与技术学院',
            'phone': '13800138001',
            'is_active': True,
        }
    )
    if created:
        teacher_user.set_password('teacher123')
        teacher_user.save()
        
        # 创建教师档案
        TeacherProfile.objects.get_or_create(
            user=teacher_user,
            defaults={
                'title': 'professor',
                'research_area': '人工智能与机器学习',
                'office_location': '计算机楼502室',
                'teaching_experience': 15,
                'education_background': '博士研究生',
                'is_active_teacher': True,
            }
        )
        test_accounts.append(('test_teacher', 'teacher123', '张教授'))
    
    # 创建测试学生账号
    student_user, created = User.objects.get_or_create(
        username='test_student',
        defaults={
            'email': 'student@university.edu.cn',
            'first_name': '李',
            'last_name': '明',
            'user_type': 'student',
            'student_id': 'S2024001001',
            'department': '计算机科学与技术学院',
            'phone': '13900139001',
            'is_active': True,
        }
    )
    if created:
        student_user.set_password('student123')
        student_user.save()
        
        # 创建学生档案
        StudentProfile.objects.get_or_create(
            user=student_user,
            defaults={
                'admission_year': 2024,
                'major': '计算机科学与技术',
                'class_name': '计算机科学与技术1班',
                'gpa': Decimal('3.8'),
                'total_credits': 120,
                'completed_credits': 45,
                'enrollment_status': 'active',
            }
        )
        test_accounts.append(('test_student', 'student123', '李明同学'))
    
    # 创建额外的测试账号
    for i in range(2, 6):  # 创建teacher2-teacher5, student2-student5
        # 测试教师
        teacher_username = f'teacher{i}'
        teacher_user, created = User.objects.get_or_create(
            username=teacher_username,
            defaults={
                'email': f'{teacher_username}@university.edu.cn',
                'first_name': f'教师{i}',
                'last_name': '老师',
                'user_type': 'teacher',
                'employee_id': f'T00100{i}',
                'department': random.choice(['计算机科学与技术学院', '电子信息工程学院', '数学与统计学院']),
                'is_active': True,
            }
        )
        if created:
            teacher_user.set_password('teacher123')
            teacher_user.save()
            TeacherProfile.objects.get_or_create(
                user=teacher_user,
                defaults={
                    'title': random.choice(['lecturer', 'associate_professor', 'professor']),
                    'research_area': '专业研究领域',
                    'office_location': f'教学楼{random.randint(100, 599)}室',
                    'teaching_experience': random.randint(3, 20),
                    'education_background': '博士研究生',
                    'is_active_teacher': True,
                }
            )
            test_accounts.append((teacher_username, 'teacher123', f'教师{i}老师'))
        
        # 测试学生
        student_username = f'student{i}'
        student_user, created = User.objects.get_or_create(
            username=student_username,
            defaults={
                'email': f'{student_username}@university.edu.cn',
                'first_name': f'学生{i}',
                'last_name': '同学',
                'user_type': 'student',
                'student_id': f'S202400100{i}',
                'department': random.choice(['计算机科学与技术学院', '电子信息工程学院', '数学与统计学院']),
                'is_active': True,
            }
        )
        if created:
            student_user.set_password('student123')
            student_user.save()
            StudentProfile.objects.get_or_create(
                user=student_user,
                defaults={
                    'admission_year': 2024,
                    'major': random.choice(['计算机科学与技术', '软件工程', '电子信息工程']),
                    'class_name': f'专业{i}班',
                    'gpa': Decimal(str(round(random.uniform(2.0, 4.0), 2))),
                    'total_credits': 120,
                    'completed_credits': random.randint(20, 80),
                    'enrollment_status': 'active',
                }
            )
            test_accounts.append((student_username, 'student123', f'学生{i}同学'))
    
    print(f"   ✅ 创建 {len(test_accounts)} 个测试账号")
    return test_accounts

@transaction.atomic
def import_data():
    """主导入函数"""
    print("🚀 开始导入生成的测试数据...")
    print("=" * 60)
    
    # 1. 加载数据
    data = load_generated_data()
    if not data:
        return
    
    # 2. 处理院系
    dept_names = create_departments(data['departments'])
    
    # 3. 创建学生
    students_count = create_students(data['students'], data['majors'], dept_names)
    
    # 4. 创建教师
    teachers_count = create_teachers(data['teachers'], dept_names)
    
    # 5. 创建课程
    courses_count = create_courses(data['courses'], dept_names)
    
    # 6. 创建选课记录
    enrollments_count = create_enrollments(data.get('enrollments', []))
    
    # 7. 创建特定测试账号
    test_accounts = create_test_accounts()
    
    print("\n" + "=" * 60)
    print("🎉 数据导入完成!")
    print(f"📊 总计导入:")
    print(f"   - 院系: {len(dept_names)} 个")
    print(f"   - 学生: {students_count} 人")
    print(f"   - 教师: {teachers_count} 人") 
    print(f"   - 课程: {courses_count} 门")
    print(f"   - 选课记录: {enrollments_count} 条")
    print(f"   - 测试账号: {len(test_accounts)} 个")
    
    print("\n🔑 测试账号信息:")
    for username, password, name in test_accounts:
        print(f"   - {name}: {username} / {password}")
    
    print("=" * 60)

if __name__ == '__main__':
    import_data()