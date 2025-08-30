#!/usr/bin/env python
"""
直接生成大量测试数据脚本
不依赖外部JSON文件，直接在Django中生成几万条数据
"""
import os
import django
import random
from datetime import datetime, date
from decimal import Decimal

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Building, Classroom
from apps.schedules.models import TimeSlot

User = get_user_model()

# 预定义数据
DEPARTMENTS = [
    '计算机科学与技术学院', '软件学院', '信息工程学院', 
    '数学与统计学院', '物理学院', '化学学院',
    '生物科学学院', '经济管理学院', '外国语学院', '文学院'
]

MAJORS = [
    '计算机科学与技术', '软件工程', '网络工程', '信息安全',
    '数据科学与大数据技术', '人工智能', '物联网工程',
    '数学与应用数学', '统计学', '应用物理学', '化学',
    '生物技术', '工商管理', '会计学', '英语', '汉语言文学'
]

COURSE_NAMES = [
    'Python程序设计', '数据结构与算法', '计算机网络', '数据库系统原理',
    '操作系统', '软件工程', '机器学习', '深度学习', '人工智能导论',
    'Web开发技术', '移动应用开发', '信息安全', '计算机图形学',
    '编译原理', '计算机组成原理', '离散数学', '概率论与数理统计',
    '线性代数', '高等数学', '大学物理', '大学英语', '马克思主义基本原理'
]

FIRST_NAMES = [
    '张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴',
    '徐', '孙', '马', '朱', '胡', '林', '郭', '何', '高', '罗'
]

LAST_NAMES = [
    '伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋',
    '勇', '艳', '杰', '涛', '明', '超', '秀英', '霞', '平', '刚',
    '桂英', '建华', '建国', '建军', '志强', '志明', '秀兰', '秀珍'
]

def generate_name():
    """生成随机姓名"""
    return random.choice(FIRST_NAMES) + random.choice(LAST_NAMES)

def generate_phone():
    """生成随机手机号"""
    return f"1{random.choice([3,4,5,7,8,9])}{random.randint(10000000, 99999999)}"

def create_large_dataset():
    """创建大量测试数据"""
    print("🚀 开始生成大量测试数据...")
    print("=" * 60)
    
    # 预计算密码哈希
    student_password = make_password('student123')
    teacher_password = make_password('teacher123')
    
    with transaction.atomic():
        # 1. 创建教学楼和教室
        print("🏢 创建教学楼和教室...")
        buildings = []
        for i in range(1, 11):  # 10栋教学楼
            building, created = Building.objects.get_or_create(
                name=f'教学楼{i}号',
                defaults={
                    'code': f'BUILD{i:02d}',
                    'address': f'校园{i}区',
                    'description': f'第{i}教学楼'
                }
            )
            if created:
                buildings.append(building)
        
        # 为每栋楼创建教室
        classroom_count = 0
        for building in buildings:
            for floor in range(1, 6):  # 5层
                for room in range(1, 21):  # 每层20间教室
                    room_number = f'{floor}{room:02d}'
                    classroom, created = Classroom.objects.get_or_create(
                        building=building,
                        room_number=room_number,
                        defaults={
                            'name': f'{building.name}{room_number}',
                            'capacity': random.randint(30, 120),
                            'floor': floor,
                            'room_type': random.choice(['lecture', 'lab', 'seminar']),
                            'equipment': {
                                'projector': True,
                                'audio': random.choice([True, False]),
                                'ac': True,
                                'computer': random.choice([True, False])
                            },
                            'is_available': True
                        }
                    )
                    if created:
                        classroom_count += 1
        
        print(f"   ✅ 创建 {len(buildings)} 栋教学楼，{classroom_count} 间教室")
        
        # 2. 创建时间段
        print("⏰ 创建时间段...")
        from datetime import time

        time_slots_data = [
            ('第1节', time(8, 0), time(8, 45), 1),
            ('第2节', time(8, 55), time(9, 40), 2),
            ('第3节', time(10, 0), time(10, 45), 3),
            ('第4节', time(10, 55), time(11, 40), 4),
            ('第5节', time(14, 0), time(14, 45), 5),
            ('第6节', time(14, 55), time(15, 40), 6),
            ('第7节', time(16, 0), time(16, 45), 7),
            ('第8节', time(16, 55), time(17, 40), 8),
            ('第9节', time(19, 0), time(19, 45), 9),
            ('第10节', time(19, 55), time(20, 40), 10),
        ]

        time_slots = []
        for name, start, end, order in time_slots_data:
            slot, created = TimeSlot.objects.get_or_create(
                name=name,
                defaults={
                    'start_time': start,
                    'end_time': end,
                    'order': order,
                    'is_active': True
                }
            )
            if created:
                time_slots.append(slot)
        
        print(f"   ✅ 创建 {len(time_slots)} 个时间段")
        
        # 3. 创建教师用户
        print("👨‍🏫 创建教师用户...")
        teacher_count = 0
        teachers = []
        
        for i in range(1, 1001):  # 1000个教师
            if i % 200 == 0:
                print(f"   📈 教师进度: {i}/1000 ({i/10:.1f}%)")
            
            username = f'teacher{i:04d}'
            employee_id = f'T{2024}{i:04d}'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@university.edu.cn',
                    'first_name': generate_name(),
                    'user_type': 'teacher',
                    'employee_id': employee_id,
                    'department': random.choice(DEPARTMENTS),
                    'phone': generate_phone(),
                    'is_active': True,
                    'password': teacher_password,
                }
            )
            
            if created:
                teacher_count += 1
                teachers.append(user)
                
                # 创建教师档案
                TeacherProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'title': random.choice(['assistant', 'lecturer', 'associate_professor', 'professor']),
                        'research_area': f'{user.department}相关研究',
                        'office_location': f'{user.department}大楼{random.randint(100, 999)}室',
                        'teaching_experience': random.randint(1, 25),
                        'education_background': random.choice(['硕士研究生', '博士研究生']),
                        'is_active_teacher': True,
                    }
                )
        
        print(f"   ✅ 创建 {teacher_count} 个教师用户")
        
        # 4. 创建学生用户
        print("👨‍🎓 创建学生用户...")
        student_count = 0
        students = []
        
        for i in range(1, 20001):  # 20000个学生
            if i % 2000 == 0:
                print(f"   📈 学生进度: {i}/20000 ({i/200:.1f}%)")
            
            username = f'student{i:05d}'
            student_id = f'{random.choice([2021, 2022, 2023, 2024])}{i:06d}'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@university.edu.cn',
                    'first_name': generate_name(),
                    'user_type': 'student',
                    'student_id': student_id,
                    'department': random.choice(DEPARTMENTS),
                    'phone': generate_phone(),
                    'is_active': True,
                    'password': student_password,
                }
            )
            
            if created:
                student_count += 1
                students.append(user)
                
                # 创建学生档案
                admission_year = int(student_id[:4])
                major = random.choice(MAJORS)
                
                StudentProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'admission_year': admission_year,
                        'major': major,
                        'class_name': f'{major}{random.randint(1, 5)}班',
                        'gpa': Decimal(str(round(random.uniform(2.0, 4.0), 2))),
                        'total_credits': random.randint(0, 160),
                        'completed_credits': random.randint(0, 120),
                        'enrollment_status': 'active',
                    }
                )
        
        print(f"   ✅ 创建 {student_count} 个学生用户")
        
        # 5. 创建课程
        print("📚 创建课程...")
        course_count = 0
        courses = []
        
        for i in range(1, 2001):  # 2000门课程
            if i % 400 == 0:
                print(f"   📈 课程进度: {i}/2000 ({i/20:.1f}%)")
            
            course_name = f'{random.choice(COURSE_NAMES)}{i}'
            course_code = f'CS{i:04d}'
            
            course, created = Course.objects.get_or_create(
                code=course_code,
                defaults={
                    'name': course_name,
                    'credits': random.randint(1, 6),
                    'hours': random.randint(16, 96),
                    'course_type': random.choice(['required', 'elective', 'public']),
                    'department': random.choice(DEPARTMENTS),
                    'semester': random.choice(['2024-2025-1', '2024-2025-2']),
                    'academic_year': '2024-2025',
                    'description': f'{course_name}课程描述',
                    'max_students': random.randint(30, 150),
                    'min_students': random.randint(10, 30),
                }
            )
            
            if created:
                course_count += 1
                courses.append(course)
                
                # 为课程分配教师
                if teachers:
                    selected_teachers = random.sample(teachers, min(random.randint(1, 3), len(teachers)))
                    course.teachers.set(selected_teachers)
        
        print(f"   ✅ 创建 {course_count} 门课程")
        
        # 6. 创建选课记录
        print("📝 创建选课记录...")
        enrollment_count = 0
        
        # 为每个学生随机分配课程
        for i, student in enumerate(students[:5000]):  # 限制为前5000个学生以节省时间
            if (i + 1) % 1000 == 0:
                print(f"   📈 选课进度: {i + 1}/5000 ({(i + 1)/50:.1f}%)")
            
            # 每个学生选择5-12门课程
            num_courses = random.randint(5, 12)
            selected_courses = random.sample(courses, min(num_courses, len(courses)))
            
            for course in selected_courses:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'status': random.choice(['enrolled', 'completed']),
                        'score': Decimal(str(random.randint(60, 100))) if random.choice([True, False]) else None,
                        'grade': random.choice(['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', '']) if random.choice([True, False]) else '',
                    }
                )
                
                if created:
                    enrollment_count += 1
        
        print(f"   ✅ 创建 {enrollment_count} 条选课记录")
    
    print("\n" + "=" * 60)
    print("🎉 大量测试数据生成完成！")
    print(f"📊 数据统计:")
    print(f"   - 教师: {User.objects.filter(user_type='teacher').count():,} 人")
    print(f"   - 学生: {User.objects.filter(user_type='student').count():,} 人")
    print(f"   - 课程: {Course.objects.count():,} 门")
    print(f"   - 教室: {Classroom.objects.count():,} 间")
    print(f"   - 选课记录: {Enrollment.objects.count():,} 条")
    print(f"   - 总用户数: {User.objects.count():,} 个")
    
    print("\n🔑 测试账户信息:")
    print("   管理员: admin / admin123")
    print("   教师: teacher0001-teacher1000 / teacher123")
    print("   学生: student00001-student20000 / student123")

if __name__ == '__main__':
    create_large_dataset()
