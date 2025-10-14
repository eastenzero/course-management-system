#!/usr/bin/env python
"""
增强版百万级数据生成器 - 带进度条的删除功能
解决时区警告和数据长度问题的优化版本

功能增强：
1. 带进度条的删除操作
2. 修复时区问题 (使用timezone.now())
3. 解决字段长度限制问题
4. 优化内存使用和性能
5. 完善的错误处理和回滚机制
"""

import os
import sys
import django
import gc
import time
import random
from datetime import datetime, timedelta
from typing import List
from django.utils import timezone

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.contrib.auth.hashers import make_password
from apps.courses.models import Course, Enrollment

User = get_user_model()

class EnhancedMillionDataGenerator:
    """增强版百万级数据生成器 - 带进度条删除功能"""
    
    def __init__(self):
        # 优化配置
        self.batch_size = 2000
        self.delete_batch_size = 5000  # 删除操作的批次大小
        
        # 预编译密码哈希
        self.student_password = make_password('student123')
        self.teacher_password = make_password('teacher123')
        
        # 数据配置
        self.departments = [
            '计算机学院', '软件学院', '信息学院', '人工智能学院', '网络安全学院',
            '数据科学学院', '电子工程学院', '数学学院', '物理学院', '化学学院'
        ]
        
        self.majors = [
            '计算机科学与技术', '软件工程', '信息管理', '数据科学', '人工智能',
            '网络工程', '网络安全', '电子信息工程', '通信工程', '自动化'
        ]
        
        self.subjects = [
            '高等数学', '线性代数', '概率论', '离散数学', '数据结构',
            '算法设计', '计算机组成原理', '操作系统', '计算机网络', '数据库原理',
            '软件工程', '编译原理', '人工智能', '机器学习', '深度学习'
        ]
        
        # 中文姓名数据
        self.surnames = [
            '王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
            '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗'
        ]
        
        self.given_names = [
            '伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋',
            '勇', '艳', '杰', '娟', '涛', '明', '超', '秀英', '霞', '平'
        ]
        
        self.stats = {
            'total_start_time': None,
            'students_created': 0,
            'teachers_created': 0,
            'courses_created': 0,
            'enrollments_created': 0,
            'deleted_users': 0,
            'deleted_courses': 0,
            'deleted_enrollments': 0
        }
        
    def generate_chinese_name(self):
        """生成真实中文姓名 - 限制长度以避免数据库字段限制"""
        surname = random.choice(self.surnames)
        if random.random() < 0.7:  # 70%概率双字名
            given = random.choice(self.given_names)
        else:  # 30%概率单字名
            given = random.choice(self.given_names)
        
        # 确保姓名总长度不超过字段限制 (first_name + last_name <= 30)
        full_name = surname + given
        if len(full_name) > 8:  # 保守限制
            given = given[:1]  # 只取第一个字
        
        return surname + given
    
    def generate_phone(self):
        """生成真实手机号格式"""
        prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                   '150', '151', '152', '153', '155', '156', '157', '158', '159',
                   '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
        prefix = random.choice(prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return prefix + suffix
    
    def count_existing_data(self):
        """统计现有数据量"""
        print("📊 统计现有百万级数据...")
        
        user_count = User.objects.filter(username__startswith='million_').count()
        course_count = Course.objects.filter(code__startswith='MILLION_').count()
        enrollment_count = Enrollment.objects.filter(
            student__username__startswith='million_'
        ).count()
        
        print(f"   现有用户: {user_count:,} 条")
        print(f"   现有课程: {course_count:,} 条") 
        print(f"   现有选课记录: {enrollment_count:,} 条")
        print(f"   总计: {user_count + course_count + enrollment_count:,} 条")
        
        return user_count, course_count, enrollment_count
    
    def clear_existing_million_data_with_progress(self):
        """带进度条的清理现有百万级数据"""
        print("\n🧹 开始清理现有百万级数据...")
        start_time = time.time()
        
        # 统计要删除的数据量
        user_count, course_count, enrollment_count = self.count_existing_data()
        total_to_delete = user_count + course_count + enrollment_count
        
        if total_to_delete == 0:
            print("   ✅ 没有需要清理的数据")
            return
        
        deleted_total = 0
        
        # 1. 删除选课记录（有外键依赖，需要先删除）
        if enrollment_count > 0:
            print(f"\n🗑️ 删除选课记录 ({enrollment_count:,} 条)...")
            deleted_enrollments = 0
            
            # 分批删除选课记录
            while True:
                with transaction.atomic():
                    enrollment_ids = list(
                        Enrollment.objects.filter(
                            student__username__startswith='million_'
                        ).values_list('id', flat=True)[:self.delete_batch_size]
                    )
                    
                    if not enrollment_ids:
                        break
                        
                    deleted_count = Enrollment.objects.filter(id__in=enrollment_ids).delete()[0]
                    deleted_enrollments += deleted_count
                    deleted_total += deleted_count
                    
                    # 显示进度
                    progress = (deleted_enrollments / enrollment_count) * 100
                    total_progress = (deleted_total / total_to_delete) * 100
                    print(f"   📊 选课记录删除进度: {deleted_enrollments:,}/{enrollment_count:,} ({progress:.1f}%) | 总进度: {total_progress:.1f}%")
                    
                    # 内存管理
                    if deleted_enrollments % (self.delete_batch_size * 5) == 0:
                        gc.collect()
            
            self.stats['deleted_enrollments'] = deleted_enrollments
            print(f"   ✅ 选课记录删除完成: {deleted_enrollments:,} 条")
        
        # 2. 删除课程
        if course_count > 0:
            print(f"\n🗑️ 删除课程 ({course_count:,} 条)...")
            deleted_courses = 0
            
            while True:
                with transaction.atomic():
                    course_ids = list(
                        Course.objects.filter(code__startswith='MILLION_').values_list('id', flat=True)[:self.delete_batch_size]
                    )
                    
                    if not course_ids:
                        break
                        
                    deleted_count = Course.objects.filter(id__in=course_ids).delete()[0]
                    deleted_courses += deleted_count
                    deleted_total += deleted_count
                    
                    # 显示进度
                    progress = (deleted_courses / course_count) * 100
                    total_progress = (deleted_total / total_to_delete) * 100
                    print(f"   📊 课程删除进度: {deleted_courses:,}/{course_count:,} ({progress:.1f}%) | 总进度: {total_progress:.1f}%")
                    
                    if deleted_courses % (self.delete_batch_size * 5) == 0:
                        gc.collect()
            
            self.stats['deleted_courses'] = deleted_courses
            print(f"   ✅ 课程删除完成: {deleted_courses:,} 条")
        
        # 3. 删除用户
        if user_count > 0:
            print(f"\n🗑️ 删除用户 ({user_count:,} 条)...")
            deleted_users = 0
            
            while True:
                with transaction.atomic():
                    user_ids = list(
                        User.objects.filter(username__startswith='million_').values_list('id', flat=True)[:self.delete_batch_size]
                    )
                    
                    if not user_ids:
                        break
                        
                    deleted_count = User.objects.filter(id__in=user_ids).delete()[0]
                    deleted_users += deleted_count
                    deleted_total += deleted_count
                    
                    # 显示进度
                    progress = (deleted_users / user_count) * 100
                    total_progress = (deleted_total / total_to_delete) * 100
                    print(f"   📊 用户删除进度: {deleted_users:,}/{user_count:,} ({progress:.1f}%) | 总进度: {total_progress:.1f}%")
                    
                    if deleted_users % (self.delete_batch_size * 5) == 0:
                        gc.collect()
            
            self.stats['deleted_users'] = deleted_users
            print(f"   ✅ 用户删除完成: {deleted_users:,} 条")
        
        # 强制垃圾回收
        gc.collect()
        
        elapsed = time.time() - start_time
        print(f"\n🎉 数据清理完成!")
        print(f"   删除用户: {self.stats['deleted_users']:,} 条")
        print(f"   删除课程: {self.stats['deleted_courses']:,} 条") 
        print(f"   删除选课记录: {self.stats['deleted_enrollments']:,} 条")
        print(f"   总计删除: {deleted_total:,} 条")
        print(f"   耗时: {elapsed:.1f} 秒")
    
    def generate_students(self, target_count=800000):
        """生成学生数据 - 修复时区和长度问题"""
        print(f"\n👥 开始生成 {target_count:,} 名学生用户...")
        
        created_count = 0
        start_time = time.time()
        
        for batch_start in range(0, target_count, self.batch_size):
            batch_end = min(batch_start + self.batch_size, target_count)
            batch_size = batch_end - batch_start
            
            users_to_create = []
            
            for i in range(batch_size):
                student_number = batch_start + i + 1
                name = self.generate_chinese_name()
                
                # 使用timezone.now()修复时区警告
                join_date = timezone.now() - timedelta(days=random.randint(0, 1095))
                
                user = User(
                    username=f"million_student_{student_number:08d}",
                    email=f"million_student_{student_number:08d}@university.edu.cn",
                    first_name=name[:1],  # 姓 - 限制长度
                    last_name=name[1:] if len(name) > 1 else '',  # 名 - 限制长度
                    user_type='student',
                    department=random.choice(self.departments),
                    student_id=f"S{student_number:08d}",  # 修复：简化学号格式，S+8位数字
                    phone=self.generate_phone(),
                    password=self.student_password,
                    is_active=True,
                    date_joined=join_date
                )
                users_to_create.append(user)
            
            # 批量创建 - 异常处理
            try:
                with transaction.atomic():
                    User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                    created_count += len(users_to_create)
            except Exception as e:
                print(f"   ⚠️ 学生批次 {batch_start} 创建失败: {e}")
                continue
            
            # 进度监控和内存管理
            if batch_start % (self.batch_size * 20) == 0:
                elapsed = time.time() - start_time
                progress = (created_count / target_count) * 100
                speed = created_count / elapsed if elapsed > 0 else 0
                
                print(f"   📊 学生进度: {created_count:,}/{target_count:,} ({progress:.1f}%) | "
                      f"速度: {speed:.0f} 条/秒")
                
                # 定期垃圾回收
                gc.collect()
        
        elapsed = time.time() - start_time
        self.stats['students_created'] = created_count
        print(f"   ✅ 学生生成完成: {created_count:,} 条，耗时 {elapsed:.1f} 秒")
        return created_count
    
    def generate_teachers(self, target_count=50000):
        """生成教师数据 - 修复时区和长度问题"""
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
                
                # 使用timezone.now()修复时区警告
                join_date = timezone.now() - timedelta(days=random.randint(0, 2190))
                
                user = User(
                    username=f"million_teacher_{teacher_number:06d}",
                    email=f"million_teacher_{teacher_number:06d}@university.edu.cn",
                    first_name=name[:1],  # 限制长度
                    last_name=name[1:] if len(name) > 1 else '',  # 限制长度
                    user_type='teacher',
                    department=random.choice(self.departments),
                    employee_id=f"T{teacher_number:06d}",  # 修复：简化工号格式，T+6位数字
                    phone=self.generate_phone(),
                    password=self.teacher_password,
                    is_active=True,
                    date_joined=join_date
                )
                users_to_create.append(user)
            
            try:
                with transaction.atomic():
                    User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                    created_count += len(users_to_create)
            except Exception as e:
                print(f"   ⚠️ 教师批次 {batch_start} 创建失败: {e}")
                continue
            
            if batch_start % (self.batch_size * 10) == 0:
                progress = (created_count / target_count) * 100
                print(f"   📊 教师进度: {created_count:,}/{target_count:,} ({progress:.1f}%)")
                gc.collect()
        
        elapsed = time.time() - start_time
        self.stats['teachers_created'] = created_count
        print(f"   ✅ 教师生成完成: {created_count:,} 条，耗时 {elapsed:.1f} 秒")
        return created_count

def main():
    """主函数"""
    print("🚀 增强版百万级数据生成系统")
    print("="*80)
    print(f"⏰ 开始时间: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 目标数据规模:")
    print("   - 学生用户: 800,000")
    print("   - 教师用户: 50,000")
    print("   - 课程数据: 30,000")
    print("   - 选课记录: 200,000")
    print("   - 预期总量: 1,080,000+ 条记录")
    print("="*80)
    
    generator = EnhancedMillionDataGenerator()
    generator.stats['total_start_time'] = time.time()
    
    try:
        # 1. 清理现有数据（带进度条）
        generator.clear_existing_million_data_with_progress()
        
        # 2. 生成学生数据
        generator.generate_students(800000)
        
        # 3. 生成教师数据  
        generator.generate_teachers(50000)
        
        # 最终统计
        total_elapsed = time.time() - generator.stats['total_start_time']
        total_created = (generator.stats['students_created'] + 
                        generator.stats['teachers_created'])
        
        print("\n" + "="*80)
        print("🎉 百万级数据生成完成!")
        print(f"   学生用户: {generator.stats['students_created']:,}")
        print(f"   教师用户: {generator.stats['teachers_created']:,}")
        print(f"   总计生成: {total_created:,} 条记录")
        print(f"   总耗时: {total_elapsed:.1f} 秒")
        print(f"   平均速度: {total_created/total_elapsed:.0f} 条/秒")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 生成过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main()
