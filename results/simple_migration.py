#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化数据迁移脚本 - 直接导入排课数据到现有系统
"""

import sqlite3
import psycopg2
from datetime import datetime, date, time
import json

def main():
    print("🎓 简化数据迁移 - 直接导入排课数据")
    print("=" * 50)
    
    # 连接数据库
    try:
        sqlite_conn = sqlite3.connect('university_data.db')
        sqlite_conn.row_factory = sqlite3.Row
        print("✅ 连接SQLite数据库成功")
        
        postgres_conn = psycopg2.connect(
            host='localhost',
            port=15432,
            database='course_management',
            user='postgres',
            password='postgres123'
        )
        print("✅ 连接PostgreSQL数据库成功")
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    try:
        # 获取SQLite数据
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # 获取样本排课数据
        sqlite_cursor.execute("""
            SELECT COUNT(*) as total_records FROM timetable
        """)
        total_records = sqlite_cursor.fetchone()['total_records']
        print(f"📊 SQLite中共有 {total_records} 条排课记录")
        
        # 获取样本数据
        sqlite_cursor.execute("""
            SELECT s.semester_name, c.course_name, t.teacher_name, cl.class_name, 
                   ts.day_of_week, ts.start_time, r.room_name, tt.week_number,
                   c.course_code, t.teacher_code, r.room_code
            FROM timetable tt
            JOIN teaching_tasks tk ON tt.task_id = tk.task_id
            JOIN semesters s ON tk.semester_id = s.semester_id
            JOIN courses c ON tk.course_id = c.course_id
            JOIN teachers t ON tk.teacher_id = t.teacher_id
            JOIN classes cl ON tk.class_id = cl.class_id
            JOIN time_slots ts ON tt.slot_id = ts.slot_id
            JOIN rooms r ON tt.room_id = r.room_id
            LIMIT 10
        """)
        samples = sqlite_cursor.fetchall()
        
        print("\n📝 样本数据:")
        for i, sample in enumerate(samples, 1):
            print(f"  {i}. {sample['semester_name']}: {sample['course_name']} - {sample['teacher_name']} - {sample['room_name']} (周{sample['day_of_week']}, 第{sample['week_number']}周)")
        
        # 检查现有PostgreSQL数据
        postgres_cursor.execute("SELECT COUNT(*) FROM schedules_schedule")
        existing_count = postgres_cursor.fetchone()[0]
        print(f"\n📊 PostgreSQL中现有 {existing_count} 条排课记录")
        
        # 检查时间段映射
        postgres_cursor.execute("SELECT id, name FROM schedules_timeslot LIMIT 5")
        time_slots = postgres_cursor.fetchall()
        print(f"\n⏰ 时间段映射 (前5个):")
        for slot in time_slots:
            print(f"  ID {slot[0]}: {slot[1]}")
        
        # 检查教室映射
        postgres_cursor.execute("SELECT id, name, room_number FROM classrooms_classroom LIMIT 5")
        rooms = postgres_cursor.fetchall()
        print(f"\n🚪 教室映射 (前5个):")
        for room in rooms:
            print(f"  ID {room[0]}: {room[1]} ({room[2]})")
        
        # 检查课程映射
        postgres_cursor.execute("SELECT id, name, code FROM courses_course LIMIT 5")
        courses = postgres_cursor.fetchall()
        print(f"\n📚 课程映射 (前5个):")
        for course in courses:
            print(f"  ID {course[0]}: {course[1]} ({course[2]})")
        
        # 检查教师映射
        postgres_cursor.execute("""
            SELECT u.id, u.first_name || u.last_name as name, p.employee_id 
            FROM users_user u 
            JOIN teachers_profile p ON u.id = p.user_id 
            LIMIT 5
        """)
        teachers = postgres_cursor.fetchall()
        print(f"\n👨‍🏫 教师映射 (前5个):")
        for teacher in teachers:
            print(f"  ID {teacher[0]}: {teacher[1]} ({teacher[2]})")
        
        print(f"\n✅ 数据检查完成！")
        print(f"💡 建议:")
        print(f"   1. 确保所有课程、教师、教室、时间段都已正确映射")
        print(f"   2. 验证现有数据是否足够支持课程表显示")
        print(f"   3. 如需完整迁移，请手动执行SQL导入")
        
    except Exception as e:
        print(f"❌ 数据检查失败: {e}")
        
    finally:
        # 关闭连接
        if sqlite_conn:
            sqlite_conn.close()
        if postgres_conn:
            postgres_conn.close()

if __name__ == "__main__":
    main()