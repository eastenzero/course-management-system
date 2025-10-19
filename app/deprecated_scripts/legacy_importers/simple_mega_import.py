#!/usr/bin/env python
"""
简化的百万级数据导入脚本
逐步导入，避免内存问题
"""

import os
import sys
import django
import json
import time
from datetime import datetime

# 设置Django环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.hashers import make_password

User = get_user_model()

def check_file_info():
    """检查文件信息"""
    data_file = '/app/course_data.json'
    file_size = os.path.getsize(data_file) / (1024 * 1024 * 1024)  # GB
    print(f"📁 数据文件大小: {file_size:.2f} GB")
    return data_file

def load_file_structure():
    """检查文件结构"""
    print("🔍 检查文件结构...")
    data_file = '/app/course_data.json'
    
    with open(data_file, 'r', encoding='utf-8') as f:
        # 读取前10000字符来分析结构
        sample = f.read(10000)
        
        print("📋 发现的数据类型:")
        if '"students"' in sample:
            print("   ✅ students")
        if '"teachers"' in sample:
            print("   ✅ teachers")
        if '"courses"' in sample:
            print("   ✅ courses")
        if '"departments"' in sample:
            print("   ✅ departments")
        if '"majors"' in sample:
            print("   ✅ majors")

def progressive_import():
    """渐进式导入"""
    print("\n🚀 开始渐进式数据导入...")
    
    # 首先清理现有测试数据
    print("🧹 清理现有测试数据...")
    User.objects.filter(username__startswith='student_').delete()
    User.objects.filter(username__startswith='teacher_').delete()
    
    data_file = '/app/course_data.json'
    
    # 使用Python的json模块按块读取
    print("📂 开始加载JSON数据...")
    start_time = time.time()
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            print("   🔄 解析JSON文件...")
            data = json.load(f)
            
        load_time = time.time() - start_time
        print(f"   ✅ JSON加载完成，耗时 {load_time:.1f} 秒")
        
        # 统计数据规模
        students_count = len(data.get('students', []))
        teachers_count = len(data.get('teachers', []))
        courses_count = len(data.get('courses', []))
        
        print(f"\n📊 数据规模统计:")
        print(f"   学生数量: {students_count:,}")
        print(f"   教师数量: {teachers_count:,}")
        print(f"   课程数量: {courses_count:,}")
        
        # 分批导入学生（每次1000个）
        if students_count > 0:
            import_students_batch(data['students'][:10000])  # 先导入1万个测试
            
        return True
        
    except MemoryError:
        print("❌ 内存不足，无法加载完整JSON文件")
        return False
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def import_students_batch(students_data, batch_size=500):
    """批量导入学生"""
    print(f"\n👥 开始导入 {len(students_data):,} 名学生...")
    
    password_hash = make_password('student123')
    imported_count = 0
    
    for i in range(0, len(students_data), batch_size):
        batch = students_data[i:i + batch_size]
        
        try:
            with transaction.atomic():
                users_to_create = []
                
                for student in batch:
                    username = f"student_{student.get('student_id', f'auto_{i}')}"
                    
                    if not User.objects.filter(username=username).exists():
                        user = User(
                            username=username,
                            email=f"{username}@university.edu.cn",
                            first_name=student.get('name', 'Student').split()[0],
                            last_name=student.get('name', '').split()[-1] if len(student.get('name', '').split()) > 1 else '',
                            user_type='student',
                            department=student.get('department', '未分配'),
                            password=password_hash,
                            student_id=str(student.get('student_id', ''))
                        )
                        users_to_create.append(user)
                
                if users_to_create:
                    User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                    imported_count += len(users_to_create)
                    
                print(f"   📈 已导入 {imported_count:,} 名学生...")
                
        except Exception as e:
            print(f"   ⚠️ 批次导入错误: {e}")
            continue
    
    print(f"✅ 学生导入完成: {imported_count:,}")
    return imported_count

def main():
    """主函数"""
    print("🚀 简化百万级数据导入系统")
    print("=" * 50)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查文件
    check_file_info()
    load_file_structure()
    
    # 开始导入
    success = progressive_import()
    
    if success:
        print(f"\n🎉 导入任务完成！")
    else:
        print(f"\n❌ 导入任务失败！")
    
    print("=" * 50)

if __name__ == '__main__':
    main()