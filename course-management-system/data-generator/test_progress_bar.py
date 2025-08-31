#!/usr/bin/env python3
"""
测试带进度条的数据导出功能
"""

import sys
import os
import time
import random

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generators.exporter import DataExporter, ProgressBar

def test_progress_bar():
    """测试进度条功能"""
    print("🧪 测试进度条功能")
    print("=" * 60)
    
    # 测试基本进度条
    print("\n1. 基本进度条测试")
    progress = ProgressBar(100, "基本测试")
    for i in range(100):
        time.sleep(0.02)  # 模拟处理时间
        progress.update(1)
    
    # 测试大数据进度条
    print("\n2. 大数据进度条测试")
    progress = ProgressBar(50000, "大数据处理")
    for i in range(50000):
        if i % 100 == 0:
            time.sleep(0.001)  # 模拟小延迟
        progress.update(1)
    
    print("\n✅ 进度条测试完成！")

def generate_sample_data():
    """生成示例数据用于测试导出"""
    print("\n📊 生成示例数据...")
    
    # 生成院系数据
    departments = []
    for i in range(5):
        departments.append({
            'id': i + 1,
            'name': f'计算机学院{i+1}',
            'code': f'CS{i+1:02d}',
            'dean': f'院长{i+1}',
            'phone': f'123456789{i}',
            'email': f'dean{i+1}@university.edu.cn'
        })
    
    # 生成学生数据（较大数量）
    students = []
    for i in range(10000):  # 1万学生
        students.append({
            'id': i + 1,
            'student_id': f'2024{i+1:06d}',
            'name': f'学生{i+1}',
            'gender': random.choice(['男', '女']),
            'phone': f'139{i+10000000:08d}',
            'email': f'student{i+1}@university.edu.cn',
            'major_id': random.randint(1, 10),
            'grade': 2024,
            'gpa': round(random.uniform(2.0, 4.0), 2)
        })
    
    # 生成教师数据
    teachers = []
    for i in range(500):  # 500教师
        teachers.append({
            'id': i + 1,
            'employee_id': f'T{i+1:06d}',
            'name': f'教师{i+1}',
            'phone': f'138{i+10000000:08d}',
            'email': f'teacher{i+1}@university.edu.cn',
            'department_id': random.randint(1, 5),
            'title': random.choice(['讲师', '副教授', '教授'])
        })
    
    # 生成课程数据
    courses = []
    for i in range(1000):  # 1000课程
        courses.append({
            'id': i + 1,
            'code': f'CS{i+1:04d}',
            'name': f'课程{i+1}',
            'credits': random.randint(1, 4),
            'teacher_id': random.randint(1, 500),
            'capacity': random.randint(30, 100)
        })
    
    # 生成选课记录（大量数据）
    enrollments = []
    for i in range(100000):  # 10万选课记录
        enrollments.append({
            'id': i + 1,
            'student_id': random.randint(1, 10000),
            'course_id': random.randint(1, 1000),
            'grade': random.choice(['A', 'B', 'C', 'D', 'F', '']),
            'status': 'enrolled'
        })
    
    print(f"   ✅ 生成数据完成:")
    print(f"      - 院系: {len(departments):,} 条")
    print(f"      - 学生: {len(students):,} 条") 
    print(f"      - 教师: {len(teachers):,} 条")
    print(f"      - 课程: {len(courses):,} 条")
    print(f"      - 选课记录: {len(enrollments):,} 条")
    print(f"      - 总计: {len(departments) + len(students) + len(teachers) + len(courses) + len(enrollments):,} 条")
    
    return {
        'departments': departments,
        'students': students,
        'teachers': teachers,
        'courses': courses,
        'enrollments': enrollments,
        'metadata': {
            'generated_at': '2024-08-30T19:30:00',
            'total_records': len(departments) + len(students) + len(teachers) + len(courses) + len(enrollments),
            'generator_version': '2.1.0'
        }
    }

def test_export_with_progress():
    """测试带进度条的导出功能"""
    print("\n🚀 测试带进度条的数据导出")
    print("=" * 60)
    
    # 生成测试数据
    data = generate_sample_data()
    
    # 创建导出器
    exporter = DataExporter('test_output')
    
    print("\n📤 测试JSON导出...")
    try:
        json_file = exporter.export_to_json(data, 'test_data_with_progress.json')
        print(f"✅ JSON导出成功: {json_file}")
    except Exception as e:
        print(f"❌ JSON导出失败: {e}")
    
    print("\n📤 测试SQL导出...")
    try:
        sql_file = exporter.export_to_sql(data, 'test_data_with_progress.sql')
        print(f"✅ SQL导出成功: {sql_file}")
    except Exception as e:
        print(f"❌ SQL导出失败: {e}")

def main():
    """主函数"""
    print("🧪 进度条导出功能测试")
    print("=" * 80)
    
    # 测试基本进度条
    test_progress_bar()
    
    # 测试导出功能
    test_export_with_progress()
    
    print("\n" + "=" * 80)
    print("🎉 所有测试完成!")

if __name__ == "__main__":
    main()