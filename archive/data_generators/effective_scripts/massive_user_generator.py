#!/usr/bin/env python
"""
大规模用户数据生成器 - 生成80万学生和5万教师
"""

# 设置环境变量，禁用有问题的模块
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'course_management.settings'
os.environ['DISABLE_MAGIC'] = '1'  # 禁用magic模块

import sys
import django
import random
import time
from datetime import datetime
from typing import List, Dict, Any

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# 修改magic模块导入问题
import builtins
original_import = builtins.__import__

def patched_import(name, *args, **kwargs):
    if name == 'magic':
        # 创建一个虚拟magic模块
        class FakeMagic:
            def from_buffer(self, buffer, mime=False):
                return 'application/octet-stream'
        
        class MockMagic:
            Magic = FakeMagic
            
        return MockMagic()
    return original_import(name, *args, **kwargs)

builtins.__import__ = patched_import

try:
    django.setup()
except Exception as e:
    print(f"警告: Django初始化问题: {e}")
    print("尝试继续运行...")

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password

User = get_user_model()

class MassiveUserGenerator:
    """大规模用户生成器"""
    
    def __init__(self):
        self.batch_size = 1000  # 每批处理1000个用户
        self.student_target = 800000  # 80万学生
        self.teacher_target = 50000   # 5万教师
        
        # 院系配置
        self.departments = [
            "计算机学院", "数学学院", "物理学院", "化学学院", "生物学院",
            "外国语学院", "经济管理学院", "文学院", "艺术学院", "体育学院",
            "医学院", "法学院", "教育学院", "工学院", "材料学院"
        ]
        
        # 常用姓氏
        self.surnames = [
            "王", "李", "张", "刘", "陈", "杨", "黄", "吴", "赵", "周",
            "徐", "孙", "马", "朱", "胡", "林", "郭", "何", "高", "罗",
            "郑", "梁", "谢", "宋", "唐", "许", "邓", "冯", "韩", "曹"
        ]
        
        # 常用名字
        self.given_names = [
            "伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军",
            "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞",
            "平", "刚", "桂英", "建华", "文", "华", "红", "玉兰", "建国", "英"
        ]
    
    def generate_students(self):
        """生成学生数据"""
        print(f"👨‍🎓 开始生成 {self.student_target:,} 名学生...")
        
        created_count = 0
        start_time = time.time()
        
        # 预先生成密码哈希（提高性能）
        student_password = make_password('student123')
        
        for batch_start in range(0, self.student_target, self.batch_size):
            batch_end = min(batch_start + self.batch_size, self.student_target)
            batch_users = []
            
            for i in range(batch_start, batch_end):
                # 生成用户名和学号
                student_id = f"S{2024:04d}{i+1:06d}"
                username = student_id
                
                # 生成姓名
                surname = random.choice(self.surnames)
                given_name = random.choice(self.given_names)
                if random.random() < 0.3:  # 30%概率有两个字的名字
                    given_name += random.choice(self.given_names)
                
                first_name = given_name
                last_name = surname
                
                # 生成邮箱
                email = f"{username}@university.edu.cn"
                
                # 选择院系
                department = random.choice(self.departments)
                
                # 创建用户对象
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type='student',
                    department=department,
                    student_id=student_id,
                    password=student_password,
                    is_active=True,
                    date_joined=timezone.now()
                )
                batch_users.append(user)
            
            # 批量保存
            try:
                with transaction.atomic():
                    User.objects.bulk_create(batch_users, ignore_conflicts=True)
                created_count += len(batch_users)
                
                # 显示进度
                if batch_start % (self.batch_size * 10) == 0:
                    elapsed_time = time.time() - start_time
                    speed = created_count / elapsed_time if elapsed_time > 0 else 0
                    progress = (created_count / self.student_target) * 100
                    print(f"   进度: {progress:.1f}% ({created_count:,}/{self.student_target:,}) "
                          f"速度: {speed:.0f} 学生/秒")
                
            except Exception as e:
                print(f"   批量保存失败: {e}")
                continue
        
        elapsed_time = time.time() - start_time
        print(f"✅ 学生生成完成: {created_count:,} 名，耗时 {elapsed_time:.2f} 秒")
        return created_count
    
    def generate_teachers(self):
        """生成教师数据"""
        print(f"👨‍🏫 开始生成 {self.teacher_target:,} 名教师...")
        
        created_count = 0
        start_time = time.time()
        
        # 预先生成密码哈希（提高性能）
        teacher_password = make_password('teacher123')
        
        # 教师职称
        titles = ["讲师", "副教授", "教授", "助教", "高级讲师"]
        
        for batch_start in range(0, self.teacher_target, self.batch_size):
            batch_end = min(batch_start + self.batch_size, self.teacher_target)
            batch_users = []
            
            for i in range(batch_start, batch_end):
                # 生成用户名和工号
                employee_id = f"T{2024:04d}{i+1:05d}"
                username = employee_id
                
                # 生成姓名
                surname = random.choice(self.surnames)
                given_name = random.choice(self.given_names)
                if random.random() < 0.4:  # 40%概率有两个字的名字
                    given_name += random.choice(self.given_names)
                
                first_name = given_name
                last_name = surname
                
                # 生成邮箱
                email = f"{username}@university.edu.cn"
                
                # 选择院系和职称
                department = random.choice(self.departments)
                title = random.choice(titles)
                
                # 创建用户对象
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type='teacher',
                    department=department,
                    employee_id=employee_id,
                    password=teacher_password,
                    is_active=True,
                    date_joined=timezone.now()
                )
                batch_users.append(user)
            
            # 批量保存
            try:
                with transaction.atomic():
                    User.objects.bulk_create(batch_users, ignore_conflicts=True)
                created_count += len(batch_users)
                
                # 显示进度
                if batch_start % (self.batch_size * 10) == 0:
                    elapsed_time = time.time() - start_time
                    speed = created_count / elapsed_time if elapsed_time > 0 else 0
                    progress = (created_count / self.teacher_target) * 100
                    print(f"   进度: {progress:.1f}% ({created_count:,}/{self.teacher_target:,}) "
                          f"速度: {speed:.0f} 教师/秒")
                
            except Exception as e:
                print(f"   批量保存失败: {e}")
                continue
        
        elapsed_time = time.time() - start_time
        print(f"✅ 教师生成完成: {created_count:,} 名，耗时 {elapsed_time:.2f} 秒")
        return created_count

def main():
    """主函数"""
    print("🚀 大规模用户数据生成器启动")
    print("=" * 60)
    
    # 检查当前数据状况
    current_students = User.objects.filter(user_type='student').count()
    current_teachers = User.objects.filter(user_type='teacher').count()
    
    print(f"📊 当前数据状况：")
    print(f"   学生数量: {current_students:,}")
    print(f"   教师数量: {current_teachers:,}")
    print()
    
    generator = MassiveUserGenerator()
    total_start_time = time.time()
    
    try:
        # 生成学生数据
        student_count = generator.generate_students()
        
        # 生成教师数据
        teacher_count = generator.generate_teachers()
        
        # 计算总用时
        total_time = time.time() - total_start_time
        total_created = student_count + teacher_count
        
        print("\n" + "=" * 60)
        print("🎉 大规模用户数据生成完成！")
        print(f"⏱️  总用时: {total_time:.2f} 秒 ({total_time/60:.1f} 分钟)")
        print(f"👨‍🎓 学生: {student_count:,} 名")
        print(f"👨‍🏫 教师: {teacher_count:,} 名")
        print(f"📊 总计: {total_created:,} 名用户")
        print(f"🚀 生成速度: {total_created/total_time:.0f} 用户/秒")
        
        # 验证数据
        final_students = User.objects.filter(user_type='student').count()
        final_teachers = User.objects.filter(user_type='teacher').count()
        print(f"\n🔍 验证结果:")
        print(f"   数据库学生总数: {final_students:,}")
        print(f"   数据库教师总数: {final_teachers:,}")
        print(f"   数据库用户总数: {final_students + final_teachers:,}")
        
        print("\n📋 下一步：重新运行排课数据生成器")
        print("   python intelligent_schedule_generator.py")
        
    except Exception as e:
        print(f"❌ 生成过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()