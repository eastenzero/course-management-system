#!/usr/bin/env python
"""
真正的百万级数据生成器 - 简化版
目标：生成超过100万条记录的完整数据集
"""

import os
import sys
import django
import gc
import time
import random
from datetime import datetime, date, timedelta
from typing import List

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.contrib.auth.hashers import make_password
from apps.courses.models import Course, Enrollment
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile

User = get_user_model()

class MillionDataGenerator:
    """真正的百万级数据生成器"""
    
    def __init__(self):
        self.batch_size = 2000  # 减小批次大小以节省内存
        self.student_password = make_password('student123')
        self.teacher_password = make_password('teacher123')
        
        # 预定义数据
        self.departments = [
            '计算机学院', '软件学院', '信息学院', '人工智能学院', '网络安全学院',
            '数据科学学院', '电子工程学院', '数学学院', '物理学院', '化学学院',
            '生物学院', '经济学院', '管理学院', '外语学院', '法学院'
        ]
        
        self.majors = [
            '计算机科学与技术', '软件工程', '信息管理', '数据科学', '人工智能',
            '网络工程', '网络安全', '电子信息工程', '通信工程', '自动化',
            '数学与应用数学', '统计学', '物理学', '应用物理', '化学',
            '生物技术', '经济学', '金融学', '工商管理', '市场营销',
            '英语', '日语', '法学', '国际关系', '社会学'
        ]
        
        self.subjects = [
            '高等数学', '线性代数', '概率论', '离散数学', '数据结构',
            '算法设计', '计算机组成原理', '操作系统', '计算机网络', '数据库原理',
            '软件工程', '编译原理', '人工智能', '机器学习', '深度学习',
            'Web开发', 'Java程序设计', 'Python程序设计', 'C++程序设计', 'JavaScript',
            '移动应用开发', '云计算', '大数据', '区块链', '网络安全',
            '图像处理', '自然语言处理', '计算机视觉', '机器人学', '物联网'
        ]
        
        # 中文姓氏和名字
        self.surnames = [
            '王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
            '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
            '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧'
        ]
        
        self.given_names = [
            '伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋',
            '勇', '艳', '杰', '娟', '涛', '明', '超', '秀英', '霞', '平',
            '刚', '桂英', '建华', '秀兰', '丹', '晨', '阳', '雪', '飞', '鹏',
            '欣', '悦', '婷', '雯', '琳', '萍', '红', '颖', '瑶', '慧'
        ]
        
    def generate_chinese_name(self):
        """生成中文姓名"""
        surname = random.choice(self.surnames)
        if random.random() < 0.7:  # 70%概率双字名
            given = ''.join(random.choices(self.given_names, k=2))
        else:  # 30%概率单字名
            given = random.choice(self.given_names)
        return surname + given
    
    def generate_phone(self):
        """生成手机号"""
        prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                   '150', '151', '152', '153', '155', '156', '157', '158', '159',
                   '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
        prefix = random.choice(prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return prefix + suffix
    
    def clear_existing_million_data(self):
        """清理现有的百万级数据"""
        print("🧹 清理现有百万级数据...")
        
        # 删除所有 million_ 开头的用户
        deleted_users = User.objects.filter(username__startswith='million_').delete()
        print(f"   删除用户: {deleted_users[0]} 条")
        
        # 删除所有 MILLION_ 开头的课程
        deleted_courses = Course.objects.filter(code__startswith='MILLION_').delete()
        print(f"   删除课程: {deleted_courses[0]} 条")
        
        # 强制垃圾回收
        gc.collect()
        print("   清理完成")
    
    def generate_million_students(self, target_count=800000):
        """生成百万级学生数据"""
        print(f"\n👥 开始生成 {target_count:,} 名学生...")
        
        created_count = 0
        start_time = time.time()
        
        for batch_start in range(0, target_count, self.batch_size):
            batch_end = min(batch_start + self.batch_size, target_count)
            batch_size = batch_end - batch_start
            
            users_to_create = []
            
            for i in range(batch_size):
                student_number = batch_start + i + 1
                name = self.generate_chinese_name()
                
                user = User(
                    username=f"million_student_{student_number:08d}",
                    email=f"million_student_{student_number:08d}@university.edu.cn",
                    first_name=name[:1],  # 姓
                    last_name=name[1:] if len(name) > 1 else '',  # 名
                    user_type='student',
                    department=random.choice(self.departments),
                    student_id=f"million_student_{student_number:08d}",
                    phone=self.generate_phone(),
                    password=self.student_password,
                    is_active=True,
                    date_joined=datetime.now() - timedelta(days=random.randint(0, 1095))  # 随机3年内
                )
                users_to_create.append(user)
            
            # 批量创建
            try:
                with transaction.atomic():
                    User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                    created_count += len(users_to_create)
            except Exception as e:
                print(f"   ⚠️ 批次 {batch_start} 创建失败: {e}")
                continue
            
            # 进度显示和内存管理
            if batch_start % (self.batch_size * 20) == 0:
                elapsed = time.time() - start_time
                progress = (created_count / target_count) * 100
                speed = created_count / elapsed if elapsed > 0 else 0
                
                print(f"   📊 学生进度: {created_count:,}/{target_count:,} ({progress:.1f}%) | 速度: {speed:.0f} 条/秒")
                
                # 定期垃圾回收
                gc.collect()
        
        elapsed = time.time() - start_time
        print(f"   ✅ 学生创建完成: {created_count:,} 条，耗时 {elapsed:.1f} 秒")
        return created_count
    
    def generate_million_teachers(self, target_count=50000):
        """生成教师数据"""
        print(f"\n👨‍🏫 开始生成 {target_count:,} 名教师...")
        
        created_count = 0
        start_time = time.time()
        
        for batch_start in range(0, target_count, self.batch_size):
            batch_end = min(batch_start + self.batch_size, target_count)
            batch_size = batch_end - batch_start
            
            users_to_create = []
            
            for i in range(batch_size):
                teacher_number = batch_start + i + 1
                name = self.generate_chinese_name()
                
                user = User(
                    username=f"million_teacher_{teacher_number:06d}",
                    email=f"million_teacher_{teacher_number:06d}@university.edu.cn",
                    first_name=name[:1],
                    last_name=name[1:] if len(name) > 1 else '',
                    user_type='teacher',
                    department=random.choice(self.departments),
                    employee_id=f"million_teacher_{teacher_number:06d}",
                    phone=self.generate_phone(),
                    password=self.teacher_password,
                    is_active=True,
                    date_joined=datetime.now() - timedelta(days=random.randint(0, 2190))  # 随机6年内
                )
                users_to_create.append(user)
            
            try:
                with transaction.atomic():
                    User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                    created_count += len(users_to_create)
            except Exception as e:
                print(f"   ⚠️ 批次 {batch_start} 创建失败: {e}")
                continue
            
            if batch_start % (self.batch_size * 10) == 0:
                progress = (created_count / target_count) * 100
                print(f"   📊 教师进度: {created_count:,}/{target_count:,} ({progress:.1f}%)")
                gc.collect()
        
        elapsed = time.time() - start_time
        print(f"   ✅ 教师创建完成: {created_count:,} 条，耗时 {elapsed:.1f} 秒")
        return created_count
    
    def generate_million_courses(self, target_count=30000):
        """生成课程数据"""
        print(f"\n📚 开始生成 {target_count:,} 门课程...")
        
        # 获取教师用户用于分配
        teachers = list(User.objects.filter(user_type='teacher').values_list('id', flat=True)[:10000])
        if not teachers:
            print("   ⚠️ 没有找到教师用户，跳过课程创建")
            return 0
        
        created_count = 0
        start_time = time.time()
        
        for batch_start in range(0, target_count, self.batch_size):
            batch_end = min(batch_start + self.batch_size, target_count)
            batch_size = batch_end - batch_start
            
            courses_to_create = []
            
            for i in range(batch_size):
                course_number = batch_start + i + 1
                subject = random.choice(self.subjects)
                level = random.choice(['基础', '进阶', '高级', '专业'])
                
                course = Course(
                    code=f"MILLION_{course_number:06d}",
                    name=f"{subject}({level})",
                    description=f"{subject}课程 - {level}难度，适合相关专业学生学习",
                    credits=random.choice([1, 2, 3, 4, 5]),
                    max_capacity=random.randint(20, 200),
                    instructor_id=random.choice(teachers),
                    department=random.choice(self.departments),
                    semester=random.choice(['2024春季', '2024秋季', '2025春季']),
                    academic_year=random.choice(['2023-2024', '2024-2025']),
                    is_active=True,
                    created_at=datetime.now() - timedelta(days=random.randint(0, 365))
                )
                courses_to_create.append(course)
            
            try:
                with transaction.atomic():
                    Course.objects.bulk_create(courses_to_create, ignore_conflicts=True)
                    created_count += len(courses_to_create)
            except Exception as e:
                print(f"   ⚠️ 课程批次 {batch_start} 创建失败: {e}")
                continue
            
            if batch_start % (self.batch_size * 5) == 0:
                progress = (created_count / target_count) * 100
                print(f"   📊 课程进度: {created_count:,}/{target_count:,} ({progress:.1f}%)")
        
        elapsed = time.time() - start_time
        print(f"   ✅ 课程创建完成: {created_count:,} 条，耗时 {elapsed:.1f} 秒")
        return created_count
    
    def generate_million_enrollments(self, target_count=200000):
        """生成选课记录"""
        print(f"\n📝 开始生成 {target_count:,} 条选课记录...")
        
        # 获取学生和课程ID（限制数量以节省内存）
        students = list(User.objects.filter(user_type='student', username__startswith='million_').values_list('id', flat=True)[:100000])
        courses = list(Course.objects.filter(code__startswith='MILLION_').values_list('id', flat=True))
        
        if not students or not courses:
            print("   ⚠️ 缺少学生或课程数据，跳过选课记录创建")
            return 0
        
        created_count = 0
        start_time = time.time()
        
        for batch_start in range(0, target_count, self.batch_size):
            batch_end = min(batch_start + self.batch_size, target_count)
            batch_size = batch_end - batch_start
            
            enrollments_to_create = []
            
            for i in range(batch_size):
                # 随机选择学生和课程
                student_id = random.choice(students)
                course_id = random.choice(courses)
                
                enrollment = Enrollment(
                    student_id=student_id,
                    course_id=course_id,
                    enrollment_date=datetime.now() - timedelta(days=random.randint(0, 180)),
                    status=random.choice(['enrolled', 'completed', 'dropped']),
                    grade=random.choice([None, 'A', 'B', 'C', 'D', 'F']) if random.random() > 0.3 else None
                )
                enrollments_to_create.append(enrollment)
            
            try:
                with transaction.atomic():
                    Enrollment.objects.bulk_create(enrollments_to_create, ignore_conflicts=True)
                    created_count += len(enrollments_to_create)
            except Exception as e:
                print(f"   ⚠️ 选课批次 {batch_start} 创建失败: {e}")
                continue
            
            if batch_start % (self.batch_size * 10) == 0:
                progress = (created_count / target_count) * 100
                print(f"   📊 选课进度: {created_count:,}/{target_count:,} ({progress:.1f}%)")
        
        elapsed = time.time() - start_time
        print(f"   ✅ 选课记录创建完成: {created_count:,} 条，耗时 {elapsed:.1f} 秒")
        return created_count

def main():
    """主函数 - 生成真正的百万级数据"""
    print("🚀 真正的百万级数据生成系统")
    print("=" * 80)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 目标数据规模:")
    print("   - 学生用户: 800,000")
    print("   - 教师用户: 50,000") 
    print("   - 课程数据: 30,000")
    print("   - 选课记录: 200,000")
    print("   - 预期总量: 1,080,000+ 条记录")
    print("=" * 80)
    
    generator = MillionDataGenerator()
    
    # 清理现有数据
    generator.clear_existing_million_data()
    
    total_start_time = time.time()
    
    try:
        # 分阶段生成数据
        print("\n🎯 第1阶段: 生成学生数据...")
        students_created = generator.generate_million_students(800000)
        
        print("\n🎯 第2阶段: 生成教师数据...")
        teachers_created = generator.generate_million_teachers(50000)
        
        print("\n🎯 第3阶段: 生成课程数据...")
        courses_created = generator.generate_million_courses(30000)
        
        print("\n🎯 第4阶段: 生成选课记录...")
        enrollments_created = generator.generate_million_enrollments(200000)
        
        total_created = students_created + teachers_created + courses_created + enrollments_created
        total_elapsed = time.time() - total_start_time
        
        print("\n" + "=" * 80)
        print("🎉 百万级数据生成完成！")
        print("=" * 80)
        print(f"📊 生成统计:")
        print(f"   学生用户: {students_created:,}")
        print(f"   教师用户: {teachers_created:,}")
        print(f"   课程数据: {courses_created:,}")
        print(f"   选课记录: {enrollments_created:,}")
        print(f"   总记录数: {total_created:,}")
        print(f"⏱️  总耗时: {total_elapsed/60:.1f} 分钟 ({total_elapsed:.1f} 秒)")
        print(f"⚡ 平均速度: {total_created/total_elapsed:.0f} 条/秒")
        
        # 验证数据
        print(f"\n🔍 数据验证:")
        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        grand_total = total_users + total_courses + total_enrollments
        
        print(f"   数据库总用户: {total_users:,}")
        print(f"   数据库总课程: {total_courses:,}")
        print(f"   数据库总选课: {total_enrollments:,}")
        print(f"   数据库总记录: {grand_total:,}")
        
        if grand_total >= 1000000:
            print(f"✅ 成功达到百万级数据标准！")
        else:
            print(f"⚠️ 距离百万级还差 {1000000 - grand_total:,} 条记录")
        
        return total_created
        
    except Exception as e:
        print(f"\n❌ 数据生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == '__main__':
    main()