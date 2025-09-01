#!/usr/bin/env python
"""
增强版百万级数据导入脚本
集成完整的进度监控系统，提供实时进度条、内存监控和性能统计
"""

import os
import sys
import json
import django
import gc
import psutil
from datetime import datetime, date
from decimal import Decimal
import random
import time
from typing import List, Dict, Any, Iterator
from pathlib import Path

# 导入进度监控系统
try:
    from progress_monitor import create_progress_manager
    PROGRESS_MONITOR_AVAILABLE = True
except ImportError:
    print("⚠️ 进度监控模块未找到，将使用基础进度显示")
    PROGRESS_MONITOR_AVAILABLE = False

# 设置Django环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction, connection
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.courses.models import Course, Enrollment

User = get_user_model()

class EnhancedBatchImportManager:
    """增强版批量导入管理器，集成完整进度监控"""
    
    def __init__(self, batch_size=10000, max_memory_mb=2048):
        self.batch_size = batch_size
        self.max_memory_mb = max_memory_mb
        self.imported_count = 0
        self.error_count = 0
        
        # 初始化进度管理器
        if PROGRESS_MONITOR_AVAILABLE:
            self.progress_manager = create_progress_manager(max_memory_gb=max_memory_mb/1024)
            print("🚀 进度监控系统已初始化")
        else:
            self.progress_manager = None
            print("⚠️ 使用基础进度显示模式")
        
        # 预计算密码哈希
        self.student_password_hash = make_password('student123')
        self.teacher_password_hash = make_password('teacher123')
    
    def start_monitoring(self):
        """启动进度监控"""
        if self.progress_manager:
            self.progress_manager.start_monitoring()
    
    def stop_monitoring(self):
        """停止进度监控"""
        if self.progress_manager:
            self.progress_manager.stop_monitoring()
    
    def batch_create_users(self, users_data: List[Dict], user_type: str, dept_names: List[str]) -> int:
        """批量创建用户 - 增强版进度监控"""
        created_count = 0
        total_users = len(users_data)
        current_batch_size = self.batch_size
        
        operation_name = f"{user_type}用户创建"
        print(f"\n👥 开始批量创建{user_type}用户...")
        print(f"   📊 计划创建 {total_users:,} 个{user_type}用户...")
        
        # 注册进度跟踪
        if self.progress_manager:
            self.progress_manager.register_operation(operation_name, total_users)
        
        for i in range(0, total_users, current_batch_size):
            batch = users_data[i:i + current_batch_size]
            
            # 动态调整批次大小
            if self.progress_manager:
                current_batch_size = self.progress_manager.get_optimized_batch_size(current_batch_size)
            
            try:
                with transaction.atomic():
                    batch_users = []
                    
                    for user_data in batch:
                        try:
                            if user_type == 'student':
                                username = f"student_{user_data['student_id']}"
                                unique_field = {'student_id': user_data['student_id']}
                            else:  # teacher
                                username = f"teacher_{user_data['employee_id']}"
                                unique_field = {'employee_id': user_data['employee_id']}
                            
                            if not User.objects.filter(username=username).exists():
                                user = User(
                                    username=username,
                                    email=f"{username}@university.edu.cn",
                                    first_name=user_data['name'].split()[0] if user_data['name'] else user_type.title(),
                                    last_name=user_data['name'].split()[-1] if len(user_data['name'].split()) > 1 else '',
                                    user_type=user_type,
                                    department=random.choice(dept_names) if dept_names else '未分配',
                                    phone=user_data.get('phone', ''),
                                    is_active=user_data.get('is_active', True),
                                    password=self.student_password_hash if user_type == 'student' else self.teacher_password_hash,
                                    **unique_field
                                )
                                batch_users.append(user)
                        except Exception as e:
                            self.error_count += 1
                            continue
                    
                    if batch_users:
                        User.objects.bulk_create(batch_users, ignore_conflicts=True)
                        created_count += len(batch_users)
                
                # 更新进度
                current_progress = min(i + current_batch_size, total_users)
                if self.progress_manager:
                    self.progress_manager.update_progress(operation_name, current_progress, self.error_count)
                else:
                    percentage = (current_progress / total_users) * 100
                    print(f"   进度: {current_progress:,}/{total_users:,} ({percentage:.1f}%)")
                
                # 内存管理
                if self.progress_manager and self.progress_manager.should_force_gc():
                    self.progress_manager.force_gc()
                elif i % (current_batch_size * 5) == 0:
                    gc.collect()
                    
            except Exception as e:
                print(f"   ❌ 批量创建{user_type}用户失败: {e}")
                self.error_count += len(batch)
                continue
        
        print(f"   ✅ 成功创建 {created_count:,} 个{user_type}用户")
        return created_count

def load_generated_data():
    """加载生成的JSON数据"""
    possible_paths = [
        '/app/course_data.json',
        'optimized_large_output/json/course_data.json',
        'conservative_large_output/json/course_data.json',
    ]
    
    for data_file in possible_paths:
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ 成功加载数据文件，总计 {data['metadata']['total_records']:,} 条记录")
                return data
            except Exception as e:
                print(f"❌ 读取文件时出错: {e}")
                continue
    
    print("❌ 未找到任何数据文件")
    return None

def main():
    """主函数"""
    start_time = time.time()
    
    print("🚀 增强版百万级数据导入系统启动")
    print("=" * 80)
    
    # 加载数据
    data = load_generated_data()
    if not data:
        print("❌ 无法加载数据文件，退出程序")
        return
    
    # 初始化导入管理器
    import_manager = EnhancedBatchImportManager(batch_size=5000, max_memory_mb=2048)
    
    try:
        # 启动进度监控系统
        import_manager.start_monitoring()
        
        print(f"\n🎬 开始百万级数据导入...")
        print(f"📊 数据规模: 总计 {data['metadata']['total_records']:,} 条记录")
        
        # 处理院系数据
        dept_names = [dept['name'] for dept in data['departments']]
        print(f"📚 处理 {len(dept_names)} 个院系")
        
        # 批量创建学生用户
        students_count = import_manager.batch_create_users(
            data['students'], 'student', dept_names
        )
        
        # 批量创建教师用户  
        teachers_count = import_manager.batch_create_users(
            data['teachers'], 'teacher', dept_names
        )
        
        # 计算总导入时间
        end_time = time.time()
        duration = end_time - start_time
        
        # 停止进度监控系统
        import_manager.stop_monitoring()
        
        # 输出最终统计
        print("\n" + "=" * 80)
        print("🎉 百万级数据导入完成！")
        print("=" * 80)
        print(f"📊 导入统计:")
        print(f"   👥 学生用户: {students_count:,}")
        print(f"   👨‍🏫 教师用户: {teachers_count:,}")
        print(f"   📊 总记录数: {students_count + teachers_count:,}")
        print(f"   ⏱️  总用时: {duration:.2f} 秒")
        print(f"   🚀 导入速度: {(students_count + teachers_count) / duration:.0f} 条/秒")
        print(f"   ❌ 错误数: {import_manager.error_count}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 导入过程中发生错误: {e}")
        import_manager.stop_monitoring()
        return
    
    print("✅ 增强版百万级数据导入任务完成！")

if __name__ == "__main__":
    main()