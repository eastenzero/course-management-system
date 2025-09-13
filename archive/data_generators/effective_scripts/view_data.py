#!/usr/bin/env python3
"""
数据库数据查看脚本 - 直观显示数据内容
"""

import psycopg2
from datetime import datetime

def view_database_data():
    """查看数据库数据"""
    print("🔍 数据库数据查看器")
    print("=" * 80)
    
    try:
        # 连接数据库
        connection = psycopg2.connect(
            host="localhost",
            port="15432", 
            database="course_management",
            user="postgres",
            password="postgres123"
        )
        print("✅ 数据库连接成功")
        cursor = connection.cursor()
        
        # 1. 查看用户数据示例
        print("\n👥 用户数据示例（前10条）:")
        print("-" * 80)
        cursor.execute("""
            SELECT 
                id, username, first_name, last_name, email, user_type, date_joined::date
            FROM users_user 
            ORDER BY id 
            LIMIT 10
        """)
        users = cursor.fetchall()
        
        print(f"{'ID':<6} {'用户名':<20} {'姓名':<15} {'邮箱':<25} {'类型':<10} {'注册日期'}")
        print("-" * 80)
        for user in users:
            user_id, username, first_name, last_name, email, user_type, date_joined = user
            full_name = f"{first_name} {last_name}".strip()
            print(f"{user_id:<6} {username:<20} {full_name:<15} {email:<25} {user_type:<10} {date_joined}")
        
        # 2. 查看学生用户示例
        print("\n📚 学生用户示例（前10条）:")
        print("-" * 80)
        cursor.execute("""
            SELECT 
                id, username, first_name, last_name, email
            FROM users_user 
            WHERE user_type = 'student'
            ORDER BY id 
            LIMIT 10
        """)
        students = cursor.fetchall()
        
        print(f"{'ID':<6} {'学生用户名':<20} {'姓名':<15} {'邮箱':<30}")
        print("-" * 80)
        for student in students:
            student_id, username, first_name, last_name, email = student
            full_name = f"{first_name} {last_name}".strip()
            print(f"{student_id:<6} {username:<20} {full_name:<15} {email:<30}")
        
        # 3. 查看教师用户示例
        print("\n👨‍🏫 教师用户示例（前10条）:")
        print("-" * 80)
        cursor.execute("""
            SELECT 
                id, username, first_name, last_name, email
            FROM users_user 
            WHERE user_type = 'teacher'
            ORDER BY id 
            LIMIT 10
        """)
        teachers = cursor.fetchall()
        
        print(f"{'ID':<6} {'教师用户名':<20} {'姓名':<15} {'邮箱':<30}")
        print("-" * 80)
        for teacher in teachers:
            teacher_id, username, first_name, last_name, email = teacher
            full_name = f"{first_name} {last_name}".strip()
            print(f"{teacher_id:<6} {username:<20} {full_name:<15} {email:<30}")
        
        # 4. 查看课程数据
        print("\n📖 课程数据:")
        print("-" * 80)
        cursor.execute("""
            SELECT 
                id, name, code, credits, course_type, semester, max_students, is_active
            FROM courses_course 
            ORDER BY id
        """)
        courses = cursor.fetchall()
        
        if courses:
            print(f"{'ID':<4} {'课程名称':<20} {'课程代码':<10} {'学分':<4} {'类型':<10} {'学期':<10} {'最大人数':<6} {'状态'}")
            print("-" * 80)
            for course in courses:
                course_id, name, code, credits, course_type, semester, max_students, is_active = course
                status = "激活" if is_active else "禁用"
                print(f"{course_id:<4} {name:<20} {code:<10} {credits:<4} {course_type:<10} {semester:<10} {max_students:<6} {status}")
        else:
            print("暂无课程数据")
        
        # 5. 查看教室数据
        print("\n🏫 教室数据:")
        print("-" * 80)
        cursor.execute("""
            SELECT 
                id, name, capacity, room_type, is_available
            FROM classrooms_classroom 
            ORDER BY id
        """)
        classrooms = cursor.fetchall()
        
        if classrooms:
            print(f"{'ID':<4} {'教室名称':<20} {'容量':<6} {'类型':<15} {'可用状态'}")
            print("-" * 80)
            for classroom in classrooms:
                room_id, name, capacity, room_type, is_available = classroom
                status = "可用" if is_available else "不可用"
                print(f"{room_id:<4} {name:<20} {capacity:<6} {room_type:<15} {status}")
        else:
            print("暂无教室数据")
        
        # 6. 查看学生档案
        print("\n📋 学生档案示例（前5条）:")
        print("-" * 80)
        cursor.execute("""
            SELECT 
                sp.id, u.username, sp.student_id, sp.major_name, sp.year, sp.phone
            FROM students_profile sp
            JOIN users_user u ON sp.user_id = u.id
            ORDER BY sp.id
            LIMIT 5
        """)
        student_profiles = cursor.fetchall()
        
        if student_profiles:
            print(f"{'ID':<4} {'用户名':<20} {'学号':<15} {'专业':<15} {'年级':<4} {'电话'}")
            print("-" * 80)
            for profile in student_profiles:
                profile_id, username, student_id, major, year, phone = profile
                print(f"{profile_id:<4} {username:<20} {student_id:<15} {major:<15} {year:<4} {phone or 'N/A'}")
        else:
            print("暂无学生档案数据")
        
        # 7. 查看教师档案
        print("\n👨‍🏫 教师档案示例:")
        print("-" * 80)
        cursor.execute("""
            SELECT 
                tp.id, u.username, tp.employee_id, tp.department_name, tp.title, tp.phone
            FROM teachers_profile tp
            JOIN users_user u ON tp.user_id = u.id
            ORDER BY tp.id
        """)
        teacher_profiles = cursor.fetchall()
        
        if teacher_profiles:
            print(f"{'ID':<4} {'用户名':<20} {'工号':<15} {'院系':<20} {'职称':<8} {'电话'}")
            print("-" * 80)
            for profile in teacher_profiles:
                profile_id, username, employee_id, department, title, phone = profile
                print(f"{profile_id:<4} {username:<20} {employee_id:<15} {department:<20} {title:<8} {phone or 'N/A'}")
        else:
            print("暂无教师档案数据")
        
        # 8. 数据统计总结
        print("\n📊 数据统计总结:")
        print("=" * 80)
        
        # 用户统计
        cursor.execute("SELECT user_type, COUNT(*) FROM users_user GROUP BY user_type ORDER BY COUNT(*) DESC")
        user_stats = cursor.fetchall()
        
        print("用户类型分布:")
        for user_type, count in user_stats:
            print(f"  {user_type}: {count:,} 个")
        
        # 总记录统计
        tables = [
            ('users_user', '用户'),
            ('courses_course', '课程'),
            ('classrooms_classroom', '教室'),
            ('students_profile', '学生档案'),
            ('teachers_profile', '教师档案'),
            ('courses_enrollment', '选课记录')
        ]
        
        print("\n各表记录数:")
        total_records = 0
        for table_name, table_desc in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                total_records += count
                print(f"  {table_desc}: {count:,} 条")
            except:
                print(f"  {table_desc}: 查询失败")
        
        print(f"\n总记录数: {total_records:,} 条")
        print(f"数据库状态: {'✅ 包含大量数据' if total_records > 100000 else '⚠️ 数据较少'}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ 查看数据失败: {e}")

if __name__ == "__main__":
    view_database_data()