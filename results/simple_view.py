#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化结果查看器 - 智能大学课程表调度系统
"""

import sqlite3
import os

def show_database_summary():
    """显示数据库统计摘要"""
    print("🗄️ 数据库统计摘要")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('university_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 主要数据统计
        tables = [
            ('colleges', '学院'),
            ('majors', '专业'),
            ('classes', '班级'),
            ('students', '学生'),
            ('teachers', '教师'),
            ('courses', '课程'),
            ('rooms', '教室'),
            ('semesters', '学期'),
            ('teaching_tasks', '教学任务'),
            ('timetable', '排课记录')
        ]
        
        for table_name, description in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            result = cursor.fetchone()
            count = result['count'] if result else 0
            print(f"📊 {description}: {count:,}")
        
        # 显示样本数据
        print("\n📋 样本数据展示")
        print("-" * 30)
        
        # 学生样本
        cursor.execute("SELECT student_name, class_id, enrollment_year FROM students LIMIT 3")
        students = cursor.fetchall()
        print("🎓 学生样本:")
        for student in students:
            print(f"  - {student['student_name']} (班级: {student['class_id']}, 入学: {student['enrollment_year']})")
        
        # 教师样本
        cursor.execute("SELECT teacher_name, department, title FROM teachers LIMIT 3")
        teachers = cursor.fetchall()
        print("\n👨‍🏫 教师样本:")
        for teacher in teachers:
            print(f"  - {teacher['teacher_name']} ({teacher['department']}, {teacher['title']})")
        
        # 课程样本
        cursor.execute("SELECT course_name, credits, course_type FROM courses LIMIT 3")
        courses = cursor.fetchall()
        print("\n📖 课程样本:")
        for course in courses:
            print(f"  - {course['course_name']} ({course['credits']}学分, {course['course_type']})")
        
        # 排课样本
        cursor.execute("""
            SELECT s.semester_name, c.course_name, t.teacher_name, cl.class_name, 
                   ts.day_of_week, ts.start_time, r.room_name, tt.week_number
            FROM timetable tt
            JOIN teaching_tasks tk ON tt.task_id = tk.task_id
            JOIN semesters s ON tk.semester_id = s.semester_id
            JOIN courses c ON tk.course_id = c.course_id
            JOIN teachers t ON tk.teacher_id = t.teacher_id
            JOIN classes cl ON tk.class_id = cl.class_id
            JOIN time_slots ts ON tt.slot_id = ts.slot_id
            JOIN rooms r ON tt.room_id = r.room_id
            LIMIT 3
        """)
        timetable_samples = cursor.fetchall()
        print("\n📅 排课样本:")
        for item in timetable_samples:
            print(f"  - {item['semester_name']}: {item['course_name']} by {item['teacher_name']}")
            print(f"    班级: {item['class_name']}, 时间: {item['day_of_week']} {item['start_time']}, 教室: {item['room_name']}, 第{item['week_number']}周")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库查看失败: {e}")

def show_file_info():
    """显示文件信息"""
    print("\n📁 结果文件信息")
    print("=" * 50)
    
    files_info = [
        ('comprehensive_timetable.xlsx', '📊 主要排课结果报表', 'xlsx'),
        ('university_timetable_system.xlsx', '📋 基础数据报表', 'xlsx'),
        ('university_data.db', '💾 SQLite完整数据库', 'db'),
        ('university_data.sql', '🏗️ 基础数据结构', 'sql'),
        ('timetable_data.sql', '📅 排课结果数据', 'sql'),
        ('README.md', '📖 详细使用说明', 'md')
    ]
    
    for filename, description, file_type in files_info:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"
            elif file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} bytes"
            
            print(f"✅ {filename}")
            print(f"   📋 {description}")
            print(f"   📏 大小: {size_str}")
            
            if file_type == 'sql':
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('--'):
                            print(f"   📝 说明: {first_line[2:].strip()}")
                except:
                    pass
            elif file_type == 'xlsx':
                print(f"   🎯 用途: 数据分析和报表查看")
            elif file_type == 'db':
                print(f"   🎯 用途: 数据库存储和查询")
            elif file_type == 'md':
                print(f"   🎯 用途: 详细使用文档")
        else:
            print(f"❌ {filename}: 文件不存在")
        print()

def main():
    """主函数"""
    print("🎓 智能大学课程表调度系统 - 结果查看器")
    print("=" * 60)
    
    # 显示当前目录
    current_dir = os.getcwd()
    print(f"📁 当前目录: {current_dir}")
    print(f"📊 发现 {len([f for f in os.listdir('.') if os.path.isfile(f)])} 个文件")
    print()
    
    # 显示文件信息
    show_file_info()
    
    print("=" * 60)
    
    # 显示数据库摘要
    if os.path.exists('university_data.db'):
        show_database_summary()
    else:
        print("❌ 数据库文件未找到")
    
    print("\n" + "=" * 60)
    print("💡 快速使用指南:")
    print("1. 📊 打开 comprehensive_timetable.xlsx 查看完整排课结果")
    print("2. 🗄️ 使用 university_data.db 进行数据库查询")
    print("3. 📖 查看 README.md 获取详细使用说明")
    print("4. 🎯 所有文件已整理完毕，可直接使用！")
    print("\n✅ 智能排课系统结果查看完成！")

if __name__ == "__main__":
    main()