#!/usr/bin/env python
"""
流式百万级数据导入脚本
使用流式JSON解析，避免内存溢出
"""

import os
import sys
import django
import json
import gc
from datetime import datetime
from typing import Iterator, Dict, Any

# 设置Django环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.hashers import make_password
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.courses.models import Course, Enrollment

User = get_user_model()

class StreamingImporter:
    """流式数据导入器"""
    
    def __init__(self, batch_size=1000):
        self.batch_size = batch_size
        self.student_password_hash = make_password('student123')
        self.teacher_password_hash = make_password('teacher123')
        
    def import_students_limit(self, limit=10000):
        """导入指定数量的学生（限制版本）"""
        print(f"\n🎓 开始导入前 {limit:,} 名学生...")
        
        data_file = '/app/course_data.json'
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                # 找到students数组开始位置
                content = f.read(1000000)  # 读取1MB用于定位
                students_start = content.find('"students":[')
                
                if students_start == -1:
                    print("❌ 未找到students数据")
                    return 0
                
                # 重新定位文件指针
                f.seek(students_start + len('"students":['))
                
                imported_count = 0
                current_batch = []
                
                # 简单的JSON数组解析
                bracket_count = 0
                current_object = ""
                in_string = False
                escape_next = False
                
                while imported_count < limit:
                    char = f.read(1)
                    if not char:
                        break
                        
                    if escape_next:
                        escape_next = False
                        current_object += char
                        continue
                        
                    if char == '\\':
                        escape_next = True
                        current_object += char
                        continue
                        
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        
                    if not in_string:
                        if char == '{':
                            bracket_count += 1
                        elif char == '}':
                            bracket_count -= 1
                            
                    current_object += char
                    
                    # 完成一个对象
                    if bracket_count == 0 and current_object.strip().endswith('}'):
                        try:
                            obj_data = json.loads(current_object.strip().rstrip(','))
                            current_batch.append(obj_data)
                            
                            # 批量处理
                            if len(current_batch) >= self.batch_size:
                                self._process_student_batch(current_batch)
                                imported_count += len(current_batch)
                                current_batch = []
                                
                                print(f"   📈 已导入 {imported_count:,} 名学生...")
                                gc.collect()
                                
                        except json.JSONDecodeError:
                            pass
                        
                        current_object = ""
                
                # 处理剩余数据
                if current_batch:
                    self._process_student_batch(current_batch)
                    imported_count += len(current_batch)
                
                print(f"✅ 成功导入 {imported_count:,} 名学生")
                return imported_count
                
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            return 0
    
    def _process_student_batch(self, batch_data):
        """处理学生批次数据"""
        try:
            with transaction.atomic():
                users_to_create = []
                
                for student in batch_data:
                    username = f"student_{student.get('student_id', 'unknown')}"
                    
                    if not User.objects.filter(username=username).exists():
                        user = User(
                            username=username,
                            email=f"{username}@university.edu.cn",
                            first_name=student.get('name', 'Student').split()[0],
                            last_name=student.get('name', '').split()[-1] if len(student.get('name', '').split()) > 1 else '',
                            user_type='student',
                            department=student.get('department', '计算机学院'),
                            phone=student.get('phone', ''),
                            is_active=True,
                            password=self.student_password_hash,
                            student_id=student.get('student_id', '')
                        )
                        users_to_create.append(user)
                
                if users_to_create:
                    User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                    
        except Exception as e:
            print(f"   ⚠️ 批次处理错误: {e}")

def main():
    """主函数"""
    print("🚀 流式百万级数据导入开始")
    print("=" * 60)
    
    importer = StreamingImporter()
    
    # 先导入10000名学生作为测试
    student_count = importer.import_students_limit(10000)
    
    print(f"\n📊 导入完成统计:")
    print(f"   学生用户: {student_count:,}")
    print("=" * 60)

if __name__ == '__main__':
    main()