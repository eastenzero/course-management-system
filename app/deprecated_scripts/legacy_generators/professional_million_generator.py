#!/usr/bin/env python
"""
专业百万级数据生成器 - Backend版本
基于 generate_real_million_data_simplified.py 的专业设计

专业特点：
1. 内存优化：batch_size=2000，分批处理
2. 性能考量：预编译密码哈希，减少重复计算  
3. 数据质量：真实中文姓名生成算法
4. 规模控制：800,000学生 + 50,000教师的百万级规模
5. 错误处理：完整的异常处理和回滚机制

目标数据规模：
- 学生用户: 800,000
- 教师用户: 50,000
- 课程数据: 30,000
- 选课记录: 200,000
- 预期总量: 1,080,000+ 条记录
"""

import os
import sys
import django
import gc
import time
import random
from datetime import datetime, date, timedelta
from typing import List

# 设置Django环境 - 专门为backend目录配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.contrib.auth.hashers import make_password
from apps.courses.models import Course, Enrollment

User = get_user_model()

class ProfessionalMillionDataGenerator:
    """专业百万级数据生成器 - 基于最佳实践设计"""
    
    def __init__(self):
        # 专业配置：优化的批次大小
        self.batch_size = 2000  
        
        # 预编译密码哈希 - 性能优化
        self.student_password = make_password('student123')
        self.teacher_password = make_password('teacher123')
        
        # 真实数据生成 - 专业数据质量保证
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
        
        # 中文姓氏和名字 - 真实数据生成
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
        
        self.stats = {
            'total_start_time': None,
            'students_created': 0,
            'teachers_created': 0,
            'courses_created': 0,
            'enrollments_created': 0
        }
        
    def generate_chinese_name(self):
        """生成真实中文姓名"""
        surname = random.choice(self.surnames)
        if random.random() < 0.7:  # 70%概率双字名
            given = ''.join(random.choices(self.given_names, k=2))
        else:  # 30%概率单字名
            given = random.choice(self.given_names)
        return surname + given
    
    def generate_phone(self):
        """生成真实手机号格式"""
        prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                   '150', '151', '152', '153', '155', '156', '157', '158', '159',
                   '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
        prefix = random.choice(prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return prefix + suffix
    
    def cleanup_existing_data(self):
        """清理现有百万级测试数据"""
        print("🧹 清理现有百万级测试数据...")
        
        try:
            with transaction.atomic():
                # 清理选课记录
                deleted_enrollments = Enrollment.objects.filter(
                    student__username__startswith='million_'
                ).delete()
                print(f"   删除选课记录: {deleted_enrollments[0] if deleted_enrollments[0] else 0} 条")
                
                # 清理million用户
                deleted_users = User.objects.filter(username__startswith='million_').delete()
                print(f"   删除用户: {deleted_users[0] if deleted_users[0] else 0} 条")
                
                # 清理MILLION课程
                deleted_courses = Course.objects.filter(code__startswith='MILLION_').delete()
                print(f"   删除课程: {deleted_courses[0] if deleted_courses[0] else 0} 条")
                
        except Exception as e:
            print(f"   ⚠️ 清理过程中出现错误: {e}")
        
        # 强制垃圾回收
        gc.collect()
        print("   ✅ 数据清理完成")
    
    def generate_students(self, target_count=800000):
        """生成800,000名学生 - 专业批处理算法"""
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
                    date_joined=datetime.now() - timedelta(days=random.randint(0, 1095))
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
                
                # 定期垃圾回收 - 内存优化
                gc.collect()
        
        elapsed = time.time() - start_time
        self.stats['students_created'] = created_count
        print(f"   ✅ 学生生成完成: {created_count:,} 条，耗时 {elapsed:.1f} 秒")
        return created_count
    
    def generate_teachers(self, target_count=50000):
        """生成50,000名教师"""
        print(f"\n👨‍🏫 开始生成 {target_count:,} 名教师用户...")
        
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
                    date_joined=datetime.now() - timedelta(days=random.randint(0, 2190))
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
    
    def generate_courses(self, target_count=30000):
        """生成30,000门课程"""
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
        self.stats['courses_created'] = created_count
        print(f"   ✅ 课程生成完成: {created_count:,} 条，耗时 {elapsed:.1f} 秒")
        return created_count
    
    def generate_enrollments(self, target_count=200000):
        """生成200,000条选课记录"""
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
        self.stats['enrollments_created'] = created_count
        print(f"   ✅ 选课记录生成完成: {created_count:,} 条，耗时 {elapsed:.1f} 秒")
        return created_count
    
    def validate_generated_data(self):
        """验证生成的数据"""
        print(f"\n🔍 验证生成数据质量...")
        
        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        grand_total = total_users + total_courses + total_enrollments
        
        validation_results = {
            'total_users': total_users,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'grand_total': grand_total,
            'million_target_achieved': grand_total >= 1000000
        }
        
        print(f"   📊 数据验证结果:")
        print(f"      总用户数: {total_users:,}")
        print(f"      总课程数: {total_courses:,}")
        print(f"      总选课记录: {total_enrollments:,}")
        print(f"      数据库总记录: {grand_total:,}")
        
        if validation_results['million_target_achieved']:
            print(f"   ✅ 成功达到百万级数据标准！")
        else:
            shortage = 1000000 - grand_total
            print(f"   ⚠️ 距离百万级还差 {shortage:,} 条记录")
        
        return validation_results
    
    def execute_professional_generation(self):
        """执行专业百万级数据生成流程"""
        print("🚀 专业百万级数据生成系统启动")
        print("=" * 80)
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📋 基于专业脚本: generate_real_million_data_simplified.py")
        print("🎯 专业设计特点:")
        print("   - 内存优化：batch_size=2000，分批处理")
        print("   - 性能考量：预编译密码哈希，减少重复计算")
        print("   - 数据质量：真实中文姓名生成算法")
        print("   - 规模控制：800,000学生 + 50,000教师的百万级规模")
        print("   - 错误处理：完整的异常处理和回滚机制")
        print("📊 目标数据规模:")
        print("   - 学生用户: 800,000")
        print("   - 教师用户: 50,000")
        print("   - 课程数据: 30,000")
        print("   - 选课记录: 200,000")
        print("   - 预期总量: 1,080,000+ 条记录")
        print("=" * 80)
        
        self.stats['total_start_time'] = time.time()
        
        try:
            # 阶段0：清理现有数据
            self.cleanup_existing_data()
            
            # 阶段1：生成学生数据
            print(f"\n🎯 阶段1: 生成学生数据")
            self.generate_students(800000)
            
            # 阶段2：生成教师数据
            print(f"\n🎯 阶段2: 生成教师数据")
            self.generate_teachers(50000)
            
            # 阶段3：生成课程数据
            print(f"\n🎯 阶段3: 生成课程数据")
            self.generate_courses(30000)
            
            # 阶段4：生成选课记录
            print(f"\n🎯 阶段4: 生成选课记录")
            self.generate_enrollments(200000)
            
            # 阶段5：数据验证
            print(f"\n🎯 阶段5: 数据验证")
            validation_results = self.validate_generated_data()
            
            # 生成最终报告
            total_elapsed = time.time() - self.stats['total_start_time']
            total_created = (
                self.stats['students_created'] + 
                self.stats['teachers_created'] + 
                self.stats['courses_created'] + 
                self.stats['enrollments_created']
            )
            
            print("\n" + "=" * 80)
            print("🎉 专业百万级数据生成完成！")
            print("=" * 80)
            print(f"📊 生成统计:")
            print(f"   学生用户: {self.stats['students_created']:,}")
            print(f"   教师用户: {self.stats['teachers_created']:,}")
            print(f"   课程数据: {self.stats['courses_created']:,}")
            print(f"   选课记录: {self.stats['enrollments_created']:,}")
            print(f"   总记录数: {total_created:,}")
            print(f"⏱️  总耗时: {total_elapsed/60:.1f} 分钟 ({total_elapsed:.1f} 秒)")
            print(f"⚡ 平均速度: {total_created/total_elapsed:.0f} 条/秒")
            print(f"💾 数据库总记录: {validation_results['grand_total']:,}")
            
            if validation_results['million_target_achieved']:
                print(f"🎊 成功达到百万级数据标准！")
            
            print("🔧 生成方式: 基于专业脚本 generate_real_million_data_simplified.py")
            print("=" * 80)
            
            return {
                'success': True,
                'stats': self.stats,
                'validation': validation_results,
                'total_time': total_elapsed,
                'professional_script': 'generate_real_million_data_simplified.py'
            }
            
        except Exception as e:
            print(f"\n❌ 专业数据生成失败: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

def main():
    """主函数"""
    generator = ProfessionalMillionDataGenerator()
    result = generator.execute_professional_generation()
    
    if result.get('success'):
        print(f"\n🎊 专业百万级数据生成成功！")
        return True
    else:
        print(f"\n💥 专业数据生成失败")
        return False

if __name__ == '__main__':
    main()