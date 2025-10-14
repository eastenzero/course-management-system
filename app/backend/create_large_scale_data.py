#!/usr/bin/env python3
"""
大规模教学数据生成器
用于生成真实场景下的排课算法测试数据
"""

import os
import sys
import django
import random
from datetime import datetime, time
from decimal import Decimal
from pathlib import Path

# 设置Django环境（基于脚本位置，提升跨平台兼容性）
BASE_DIR = Path(__file__).resolve().parent  # app/backend
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.users.models import User
from apps.classrooms.models import Classroom, Building
from apps.schedules.models import Schedule, TimeSlot
from apps.courses.models import Course, Enrollment

User = get_user_model()

class LargeScaleDataGenerator:
    """大规模数据生成器"""
    
    def __init__(self):
        self.semester = "2024春"
        self.academic_year = "2023-2024"
        
        # 专业设置
        self.departments = {
            'computer': '计算机科学与技术学院',
            'math': '数学与统计学院',
            'physics': '物理与电子工程学院',
            'chemistry': '化学与材料科学学院',
            'biology': '生物与医学工程学院',
            'economics': '经济与管理学院',
            'foreign': '外国语学院',
            'literature': '文学与新闻传播学院',
            'mechanical': '机械与动力工程学院',
            'electrical': '电气与自动化工程学院'
        }
        
        # 课程类型
        self.course_types = {
            'required': {'name': '必修', 'weight': 0.4},
            'elective': {'name': '选修', 'weight': 0.3},
            'general': {'name': '通识', 'weight': 0.2},
            'practice': {'name': '实践', 'weight': 0.1}
        }
        
        # 时间段配置
        self.time_slots = [
            {'order': 1, 'start': '08:00', 'end': '08:45'},
            {'order': 2, 'start': '08:55', 'end': '09:40'},
            {'order': 3, 'start': '10:00', 'end': '10:45'},
            {'order': 4, 'start': '10:55', 'end': '11:40'},
            {'order': 5, 'start': '14:00', 'end': '14:45'},
            {'order': 6, 'start': '14:55', 'end': '15:40'},
            {'order': 7, 'start': '16:00', 'end': '16:45'},
            {'order': 8, 'start': '16:55', 'end': '17:40'},
            {'order': 9, 'start': '19:00', 'end': '19:45'},
            {'order': 10, 'start': '19:55', 'end': '20:40'}
        ]
        
        # 星期配置
        self.week_days = [1, 2, 3, 4, 5]  # 周一到周五
        
        # 教学楼配置
        self.buildings = [
            {'code': 'A', 'name': '教学楼A', 'floors': 5},
            {'code': 'B', 'name': '教学楼B', 'floors': 4},
            {'code': 'C', 'name': '教学楼C', 'floors': 3},
            {'code': 'D', 'name': '实验楼D', 'floors': 4},
            {'code': 'E', 'name': '工程楼E', 'floors': 6}
        ]
        
        # 教室类型
        self.classroom_types = {
            'lecture': {'name': '多媒体教室', 'capacity_range': (60, 200)},
            'lab': {'name': '实验室', 'capacity_range': (30, 80)},
            'computer': {'name': '计算机房', 'capacity_range': (40, 120)},
            'language': {'name': '语音室', 'capacity_range': (30, 60)},
            'meeting': {'name': '会议室', 'capacity_range': (20, 50)}
        }

    def generate_courses(self, count=80):
        """生成课程数据"""
        print(f"开始生成 {count} 门课程...")
        
        # 课程池
        course_pool = {
            'computer': [
                ('高等数学A', 4, 64), ('高等数学B', 3, 48), ('线性代数', 3, 48), ('概率论', 3, 48),
                ('程序设计基础', 4, 64), ('数据结构', 4, 64), ('算法设计与分析', 3, 48),
                ('计算机组成原理', 3, 48), ('操作系统', 3, 48), ('数据库系统', 3, 48),
                ('计算机网络', 3, 48), ('软件工程', 3, 48), ('人工智能导论', 2, 32),
                ('机器学习', 3, 48), ('深度学习', 3, 48), ('计算机视觉', 3, 48),
                ('自然语言处理', 3, 48), ('云计算技术', 2, 32), ('大数据分析', 3, 48),
                ('区块链技术', 2, 32), ('移动应用开发', 3, 48), ('Web开发技术', 3, 48)
            ],
            'math': [
                ('数学分析', 5, 80), ('高等代数', 4, 64), ('解析几何', 3, 48),
                ('常微分方程', 3, 48), ('偏微分方程', 3, 48), ('复变函数', 3, 48),
                ('实变函数', 3, 48), ('泛函分析', 3, 48), ('拓扑学', 3, 48),
                ('微分几何', 3, 48), ('数值分析', 3, 48), ('运筹学', 3, 48),
                ('统计学原理', 3, 48), ('随机过程', 3, 48), ('时间序列分析', 3, 48)
            ],
            'physics': [
                ('力学', 4, 64), ('热学', 3, 48), ('电磁学', 4, 64), ('光学', 3, 48),
                ('原子物理', 3, 48), ('理论力学', 4, 64), ('电动力学', 4, 64),
                ('量子力学', 4, 64), ('热力学统计', 3, 48), ('固体物理', 3, 48),
                ('电路分析', 3, 48), ('模拟电路', 3, 48), ('数字电路', 3, 48),
                ('信号与系统', 3, 48), ('通信原理', 3, 48)
            ],
            'chemistry': [
                ('无机化学', 4, 64), ('有机化学', 4, 64), ('分析化学', 3, 48),
                ('物理化学', 4, 64), ('结构化学', 3, 48), ('仪器分析', 3, 48),
                ('化工原理', 3, 48), ('高分子化学', 3, 48), ('生物化学', 3, 48),
                ('环境化学', 2, 32), ('材料化学', 3, 48)
            ],
            'economics': [
                ('微观经济学', 3, 48), ('宏观经济学', 3, 48), ('计量经济学', 3, 48),
                ('国际经济学', 3, 48), ('财政学', 3, 48), ('货币银行学', 3, 48),
                ('投资学', 3, 48), ('公司金融', 3, 48), ('会计学原理', 3, 48),
                ('财务管理', 3, 48), ('市场营销', 3, 48), ('管理学原理', 3, 48)
            ]
        }
        
        courses_created = 0
        
        for dept_code, dept_name in self.departments.items():
            if dept_code not in course_pool:
                continue
                
            dept_courses = course_pool[dept_code]
            courses_per_dept = count // len([d for d in self.departments.keys() if d in course_pool])
            
            for i, (name, credits, hours) in enumerate(dept_courses):
                if i >= courses_per_dept and courses_created >= count:
                    break
                    
                # 随机选择课程类型
                course_type = random.choices(
                    list(self.course_types.keys()),
                    weights=[t['weight'] for t in self.course_types.values()]
                )[0]
                
                # 生成最大学生数
                max_students = random.randint(20, 120)
                
                # 创建课程
                course, created = Course.objects.get_or_create(
                    code=f"{dept_code.upper()}{101+i:03d}",
                    defaults={
                        'name': name,
                        'credits': credits,
                        'hours': hours,
                        'max_students': max_students,
                        'course_type': course_type,
                        'department': dept_name,
                        'semester': self.semester,
                        'academic_year': self.academic_year,
                        'description': f'{name}课程，{dept_name}专业核心课程',
                        'objectives': f'掌握{name}的基本理论和方法',
                        'is_published': True,
                        'is_active': True
                    }
                )
                
                if created:
                    courses_created += 1
                    if courses_created % 10 == 0:
                        print(f'  已创建 {courses_created} 门课程')
        
        print(f'✅ 成功创建 {courses_created} 门课程')
        return courses_created

    def generate_teachers(self, count=25):
        """生成教师数据"""
        print(f"开始生成 {count} 名教师...")
        
        # 教师姓名池
        first_names = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
        last_names = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀', '兰', '玲', '平']
        
        # 专业方向
        specializations = {
            'computer': ['人工智能', '机器学习', '深度学习', '计算机视觉', '自然语言处理', '软件工程', '数据库', '网络安全', '云计算', '大数据'],
            'math': ['应用数学', '计算数学', '概率统计', '运筹学', '数值分析', '微分方程', '拓扑学', '代数学'],
            'physics': ['理论物理', '凝聚态物理', '光学', '电磁学', '量子力学', '热力学', '电路设计', '信号处理'],
            'chemistry': ['有机化学', '无机化学', '分析化学', '物理化学', '材料化学', '生物化学', '环境化学'],
            'economics': ['微观经济', '宏观经济', '金融工程', '国际贸易', '会计学', '市场营销', '管理学']
        }
        
        teachers_created = 0
        
        for i in range(count):
            # 生成姓名
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = first_name + last_name
            
            # 选择专业和方向
            dept = random.choice(list(self.departments.keys()))
            specialization = ''
            if dept in specializations:
                specialization = random.choice(specializations[dept])
            
            # 生成教师信息
            username = f"teacher_{i+1:03d}"
            email = f"{username}@university.edu.cn"
            
            # 生成工作时间和偏好
            max_weekly_hours = random.randint(12, 20)
            max_daily_hours = random.randint(4, 8)
            
            teacher, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'user_type': 'teacher',
                    'department': self.departments[dept],
                    'is_active': True
                }
            )
            
            if created:
                # 设置密码
                teacher.set_password('teacher123')
                teacher.save()
                
                teachers_created += 1
                if teachers_created % 5 == 0:
                    print(f'  已创建 {teachers_created} 名教师')
        
        print(f'✅ 成功创建 {teachers_created} 名教师')
        return teachers_created

    def generate_students(self, count=40):
        """生成学生数据"""
        print(f"开始生成 {count} 名学生...")
        
        # 学生姓名池
        first_names = ['陈', '林', '黄', '郑', '吴', '周', '徐', '孙', '胡', '朱', '高', '何', '郭', '马', '罗', '梁', '宋', '郑', '谢', '韩']
        last_names = ['小明', '小红', '小刚', '小丽', '小华', '小芳', '小强', '小娟', '小涛', '小敏', '小静', '小超', '小秀', '小兰', '小玲', '小平', '小阳', '小雨', '小雪', '小霜']
        
        # 年级和专业
        grades = ['大一', '大二', '大三', '大四']
        majors = list(self.departments.values())
        
        students_created = 0
        
        for i in range(count):
            # 生成姓名
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = first_name + last_name
            
            # 选择年级和专业
            grade = random.choice(grades)
            major = random.choice(majors)
            
            # 生成学号
            student_id = f"2024{random.randint(1000, 9999):04d}"
            username = f"student_{i+1:03d}"
            email = f"{username}@student.university.edu.cn"
            
            student, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'user_type': 'student',
                    'department': major,
                    'student_id': student_id,
                    'is_active': True
                }
            )
            
            if created:
                # 设置密码
                student.set_password('student123')
                student.save()
                
                students_created += 1
                if students_created % 10 == 0:
                    print(f'  已创建 {students_created} 名学生')
        
        print(f'✅ 成功创建 {students_created} 名学生')
        return students_created

    def generate_classrooms(self, count=30):
        """生成教室数据"""
        print(f"开始生成 {count} 间教室...")
        
        # 创建教学楼
        buildings = {}
        for building_info in self.buildings:
            building, created = Building.objects.get_or_create(
                code=building_info['code'],
                defaults={
                    'name': building_info['name'],
                    'address': f"校园{building_info['name']}"
                }
            )
            buildings[building_info['code']] = building
        
        classrooms_created = 0
        
        for i in range(count):
            # 选择教学楼和楼层
            building_code = random.choice(list(buildings.keys()))
            building = buildings[building_code]
            floor = random.randint(1, self.buildings[ord(building_code) - ord('A')]['floors'])
            
            # 选择教室类型
            room_type = random.choice(list(self.classroom_types.keys()))
            room_config = self.classroom_types[room_type]
            
            # 生成容量
            min_cap, max_cap = room_config['capacity_range']
            capacity = random.randint(min_cap, max_cap)
            
            # 生成房间号
            room_number = f"{building_code}{floor:02d}{random.randint(1, 20):02d}"
            
            # 生成设备配置
            equipment = []
            if room_type == 'lecture':
                equipment = ['projector', 'computer', 'microphone']
            elif room_type == 'lab':
                equipment = ['lab_equipment', 'projector', 'computer']
            elif room_type == 'computer':
                equipment = ['computers', 'projector', 'network']
            elif room_type == 'language':
                equipment = ['audio_system', 'headphones', 'computer']
            elif room_type == 'meeting':
                equipment = ['projector', 'whiteboard']
            
            classroom, created = Classroom.objects.get_or_create(
                room_number=room_number,
                defaults={
                    'building': building,
                    'floor': floor,
                    'capacity': capacity,
                    'room_type': room_type,
                    'equipment': equipment,
                    'is_available': True,
                    'is_active': True
                }
            )
            
            if created:
                classrooms_created += 1
                if classrooms_created % 5 == 0:
                    print(f'  已创建 {classrooms_created} 间教室')
        
        print(f'✅ 成功创建 {classrooms_created} 间教室')
        return classrooms_created

    def assign_teachers_to_courses(self):
        """为课程分配合适的教师"""
        print("开始为课程分配教师...")
        
        courses = Course.objects.filter(is_active=True)
        teachers = User.objects.filter(user_type='teacher', is_active=True)
        
        assignments_made = 0
        
        for course in courses:
            # 根据课程部门匹配教师
            course_dept = None
            for dept_code, dept_name in self.departments.items():
                if dept_name == course.department:
                    course_dept = dept_code
                    break
            
            if not course_dept:
                continue
            
            # 找到相关专业的教师
            qualified_teachers = teachers.filter(department=course.department)
            if qualified_teachers.count() < 2:
                # 如果相关专业教师不足，扩大范围
                qualified_teachers = teachers.all()
            
            # 随机分配2-3名合格教师
            num_teachers = random.randint(2, min(3, qualified_teachers.count()))
            selected_teachers = random.sample(list(qualified_teachers), num_teachers)
            
            course.teachers.set(selected_teachers)
            assignments_made += 1
            
            if assignments_made % 10 == 0:
                print(f'  已为 {assignments_made} 门课程分配教师')
        
        print(f'✅ 完成为 {assignments_made} 门课程分配教师')
        return assignments_made

    def generate_enrollments(self, courses_per_student=5):
        """生成学生选课记录"""
        print("开始生成学生选课记录...")
        
        students = User.objects.filter(user_type='student', is_active=True)
        courses = Course.objects.filter(is_active=True, is_published=True)
        
        enrollments_created = 0
        
        for student in students:
            # 根据学生专业筛选相关课程
            student_courses = courses.filter(department=student.department)
            if student_courses.count() < courses_per_student:
                # 如果专业课程不足，添加通识课程
                general_courses = courses.exclude(department=student.department)[:courses_per_student//2]
                student_courses = list(student_courses) + list(general_courses)
            
            # 随机选择课程
            available_courses = list(student_courses)
            if len(available_courses) >= courses_per_student:
                selected_courses = random.sample(available_courses, courses_per_student)
            else:
                selected_courses = available_courses
            
            # 创建选课记录
            for course in selected_courses:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'status': 'enrolled',
                        'is_active': True
                    }
                )
                
                if created:
                    enrollments_created += 1
            
            if enrollments_created % 50 == 0:
                print(f'  已创建 {enrollments_created} 条选课记录')
        
        print(f'✅ 成功创建 {enrollments_created} 条选课记录')
        return enrollments_created

    def run_generation(self, courses=80, teachers=25, students=40, classrooms=30):
        """运行完整的数据生成流程"""
        print("=" * 60)
        print("🚀 开始生成大规模教学数据")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # 1. 生成课程
            courses_created = self.generate_courses(courses)
            
            # 2. 生成教师
            teachers_created = self.generate_teachers(teachers)
            
            # 3. 生成学生
            students_created = self.generate_students(students)
            
            # 4. 生成教室
            classrooms_created = self.generate_classrooms(classrooms)
            
            # 5. 建立教学关系
            self.assign_teachers_to_courses()
            
            # 6. 生成选课
            self.generate_enrollments()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "=" * 60)
            print("🎉 大规模数据生成完成！")
            print("=" * 60)
            print(f"⏱️  总耗时: {duration:.2f}秒")
            print(f"📚 课程: {courses_created} 门")
            print(f"👨‍🏫 教师: {teachers_created} 名")
            print(f"👩‍🎓 学生: {students_created} 名")
            print(f"🏫 教室: {classrooms_created} 间")
            
            return {
                'courses': courses_created,
                'teachers': teachers_created,
                'students': students_created,
                'classrooms': classrooms_created,
                'duration': duration
            }
            
        except Exception as e:
            print(f"❌ 数据生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """主函数"""
    print("🎯 大规模教学数据生成器")
    print("专为排课算法效果检验设计")
    print("=" * 60)
    
    generator = LargeScaleDataGenerator()
    
    # 生成中等规模数据（可调整参数）
    result = generator.run_generation(
        courses=60,    # 60门课程
        teachers=20,   # 20名教师
        students=30,   # 30名学生
        classrooms=25  # 25间教室
    )
    
    if result:
        print("\n💡 下一步建议：")
        print("1. 运行排课算法生成排课方案")
        print("2. 对比不同算法的性能表现")
        print("3. 分析排课结果的质量和合理性")
        print("4. 在前端界面验证展示效果")
        
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())