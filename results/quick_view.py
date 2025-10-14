#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速查看结果脚本 - 智能大学课程表调度系统
"""

import sqlite3
import pandas as pd
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

def show_excel_files():
    """显示Excel文件信息"""
    print("\n📊 Excel文件信息")
    print("=" * 50)
    
    excel_files = [
        ('comprehensive_timetable.xlsx', '主要排课结果报表'),
        ('university_timetable_system.xlsx', '基础数据报表')
    ]
    
    for filename, description in excel_files:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"📈 {filename}")
            print(f"   描述: {description}")
            print(f"   大小: {file_size_mb:.2f} MB")
            
            try:
                # 读取工作表列表
                xl_file = pd.ExcelFile(filename)
                print(f"   工作表: {', '.join(xl_file.sheet_names)}")
            except Exception as e:
                print(f"   状态: 无法读取 - {e}")
        else:
            print(f"❌ {filename}: 文件不存在")
        print()

def show_sql_files():
    """显示SQL文件信息"""
    print("📜 SQL文件信息")
    print("=" * 50)
    
    sql_files = [
        ('university_data.sql', '基础数据库结构和数据'),
        ('timetable_data.sql', '排课结果数据')
    ]
    
    for filename, description in sql_files:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            file_size_kb = file_size / 1024
            
            print(f"🗄️ {filename}")
            print(f"   描述: {description}")
            print(f"   大小: {file_size_kb:.1f} KB")
            
            try:
                # 查看文件前几行
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:5]
                print("   预览:")
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        print(f"     {i}: {line.strip()[:80]}...")
                        if i >= 3:
                            break
            except Exception as e:
                print(f"   状态: 无法读取 - {e}")
        else:
            print(f"❌ {filename}: 文件不存在")
        print()

def main():
    """主函数"""
    print("🎓 智能大学课程表调度系统 - 结果查看器")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"📁 当前目录: {current_dir}")
    print()
    
    # 显示数据库摘要
    show_database_summary()
    
    print("\n" + "=" * 60)
    
    # 显示Excel文件信息
    show_excel_files()
    
    print("=" * 60)
    
    # 显示SQL文件信息
    show_sql_files()
    
    print("\n" + "=" * 60)
    print("💡 使用建议:")
    print("1. 📊 打开 comprehensive_timetable.xlsx 查看完整排课结果")
    print("2. 🗄️ 使用 university_data.db 进行数据库查询和分析")
    print("3. 📜 使用 SQL 文件导入其他数据库系统")
    print("4. 📋 查看 README.md 获取详细使用说明")
    print("\n✅ 所有结果文件已准备就绪！")

if __name__ == "__main__":
    main()
