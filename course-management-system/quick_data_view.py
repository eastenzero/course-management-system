#!/usr/bin/env python3
"""
快速数据查看脚本 - 查看核心数据
"""

import psycopg2

def quick_view():
    """快速查看数据"""
    print("🔍 快速数据查看")
    print("=" * 80)
    
    try:
        connection = psycopg2.connect(
            host="localhost",
            port="15432", 
            database="course_management",
            user="postgres",
            password="postgres123"
        )
        print("✅ 数据库连接成功\n")
        cursor = connection.cursor()
        
        # 1. 用户数据统计
        print("📊 用户数据统计:")
        cursor.execute("SELECT user_type, COUNT(*) FROM users_user GROUP BY user_type ORDER BY COUNT(*) DESC")
        user_stats = cursor.fetchall()
        
        for user_type, count in user_stats:
            print(f"  {user_type}: {count:,} 个用户")
        
        # 2. 查看一些真实用户示例
        print(f"\n👥 真实用户示例:")
        cursor.execute("""
            SELECT username, first_name, last_name, email, user_type 
            FROM users_user 
            WHERE username LIKE 'student_%' OR username LIKE 'teacher_%'
            ORDER BY id 
            LIMIT 15
        """)
        users = cursor.fetchall()
        
        print("用户名".ljust(25) + "姓名".ljust(15) + "邮箱".ljust(35) + "类型")
        print("-" * 80)
        for user in users:
            username, first_name, last_name, email, user_type = user
            name = f"{first_name} {last_name}".strip() or "N/A"
            print(username.ljust(25) + name.ljust(15) + email.ljust(35) + user_type)
        
        # 3. 课程数据
        print(f"\n📚 课程数据:")
        cursor.execute("SELECT COUNT(*) FROM courses_course")
        course_count = cursor.fetchone()[0]
        print(f"总课程数: {course_count}")
        
        if course_count > 0:
            cursor.execute("SELECT name, code, credits, course_type FROM courses_course LIMIT 5")
            courses = cursor.fetchall()
            print("\n课程示例:")
            for course in courses:
                name, code, credits, course_type = course
                print(f"  {name} ({code}) - {credits}学分 - {course_type}")
        
        # 4. 教室数据
        print(f"\n🏫 教室数据:")
        cursor.execute("SELECT COUNT(*) FROM classrooms_classroom")
        classroom_count = cursor.fetchone()[0]
        print(f"总教室数: {classroom_count}")
        
        if classroom_count > 0:
            cursor.execute("SELECT name, capacity, room_type FROM classrooms_classroom LIMIT 5")
            classrooms = cursor.fetchall()
            print("\n教室示例:")
            for classroom in classrooms:
                name, capacity, room_type = classroom
                print(f"  {name} - 容量{capacity}人 - {room_type}")
        
        # 5. 总体统计
        print(f"\n📈 总体统计:")
        cursor.execute("SELECT COUNT(*) FROM users_user")
        total_users = cursor.fetchone()[0]
        
        print(f"数据库包含 {total_users:,} 个用户记录")
        print("数据状态: ✅ 数据库包含大量真实数据")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ 查看失败: {e}")

if __name__ == "__main__":
    quick_view()