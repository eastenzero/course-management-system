#!/usr/bin/env python3
"""
数据验证脚本 - 检查百万级数据的导入情况和分布统计
"""

import os
import sys
import psycopg2
from datetime import datetime
import json

def get_db_connection():
    """获取数据库连接"""
    try:
        # 使用Docker映射的端口15432
        conn = psycopg2.connect(
            host="localhost",
            port="15432",
            database="course_management",
            user="course_user", 
            password="course_pass"
        )
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def check_table_counts(conn):
    """检查各表的数据量"""
    tables_info = {
        'auth_user': '用户总数',
        'courses_course': '课程总数', 
        'courses_enrollment': '选课记录总数',
        'courses_department': '院系总数',
        'courses_major': '专业总数',
        'courses_classroom': '教室总数',
        'courses_timeslot': '时间段总数',
        'courses_teacherpreference': '教师偏好总数'
    }
    
    print("📊 数据表统计信息：")
    print("=" * 60)
    
    total_records = 0
    
    for table, description in tables_info.items():
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"  {description:<15}: {count:>10,}")
            cursor.close()
        except Exception as e:
            print(f"  {description:<15}: 查询失败 ({e})")
    
    print("=" * 60)
    print(f"  总记录数: {total_records:>20,}")
    return total_records

def check_user_distribution(conn):
    """检查用户角色分布"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_type, COUNT(*) as count
            FROM auth_user 
            WHERE user_type IS NOT NULL
            GROUP BY user_type
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        
        print("\n👥 用户角色分布：")
        print("=" * 40)
        for user_type, count in results:
            print(f"  {user_type:<15}: {count:>8,}")
        
        cursor.close()
        return results
    except Exception as e:
        print(f"❌ 用户分布查询失败: {e}")
        return []

def check_course_distribution(conn):
    """检查课程类型分布"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT course_type, COUNT(*) as count
            FROM courses_course 
            GROUP BY course_type
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        
        print("\n📚 课程类型分布：")
        print("=" * 40)
        for course_type, count in results:
            print(f"  {course_type:<15}: {count:>8,}")
        
        cursor.close()
        return results
    except Exception as e:
        print(f"❌ 课程分布查询失败: {e}")
        return []

def check_enrollment_stats(conn):
    """检查选课统计信息"""
    try:
        cursor = conn.cursor()
        
        # 每名学生平均选课数
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT student_id) as total_students,
                COUNT(*) as total_enrollments,
                ROUND(COUNT(*)::decimal / COUNT(DISTINCT student_id), 2) as avg_courses_per_student
            FROM courses_enrollment
        """)
        
        stats = cursor.fetchone()
        
        print("\n📝 选课统计信息：")
        print("=" * 50)
        print(f"  参与选课学生数: {stats[0]:>12,}")
        print(f"  总选课记录数: {stats[1]:>14,}")
        print(f"  平均每人选课数: {stats[2]:>12}")
        
        # 选课数分布
        cursor.execute("""
            SELECT enrollments_per_student, COUNT(*) as student_count
            FROM (
                SELECT student_id, COUNT(*) as enrollments_per_student
                FROM courses_enrollment
                GROUP BY student_id
            ) stats
            GROUP BY enrollments_per_student
            ORDER BY enrollments_per_student
        """)
        
        distribution = cursor.fetchall()
        
        print("\n📈 选课数分布：")
        print("=" * 30)
        for courses, students in distribution:
            print(f"  选{courses}门课: {students:>6,}人")
        
        cursor.close()
        return stats, distribution
    except Exception as e:
        print(f"❌ 选课统计查询失败: {e}")
        return None, []

def check_sample_users(conn):
    """获取测试账号样本"""
    try:
        cursor = conn.cursor()
        
        # 获取各角色的示例用户
        user_samples = {}
        user_types = ['admin', 'academic_admin', 'teacher', 'student']
        
        for user_type in user_types:
            cursor.execute("""
                SELECT username, email, first_name, last_name, user_type
                FROM auth_user 
                WHERE user_type = %s
                LIMIT 5
            """, (user_type,))
            
            samples = cursor.fetchall()
            user_samples[user_type] = samples
        
        print("\n🔑 测试账号样本：")
        print("=" * 80)
        
        for user_type, samples in user_samples.items():
            print(f"\n{user_type.upper()}角色账号:")
            if samples:
                for username, email, first_name, last_name, role in samples:
                    name = f"{first_name} {last_name}".strip() or "未设置"
                    print(f"  • 用户名: {username:<15} 姓名: {name:<10} 邮箱: {email or '未设置'}")
            else:
                print("  无此角色用户")
        
        cursor.close()
        return user_samples
    except Exception as e:
        print(f"❌ 用户样本查询失败: {e}")
        return {}

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🏫 校园课程管理系统 - 数据验证报告")
    print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 连接数据库
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # 检查表记录数
        total_records = check_table_counts(conn)
        
        # 检查用户分布
        user_dist = check_user_distribution(conn)
        
        # 检查课程分布  
        course_dist = check_course_distribution(conn)
        
        # 检查选课统计
        enrollment_stats, enrollment_dist = check_enrollment_stats(conn)
        
        # 获取测试账号
        user_samples = check_sample_users(conn)
        
        # 生成总结
        print("\n" + "=" * 80)
        print("📋 验证结果总结：")
        print("=" * 80)
        
        if total_records >= 400000:
            print(f"✅ 数据规模验证通过: {total_records:,} 条记录 (≥400K)")
        else:
            print(f"❌ 数据规模不足: {total_records:,} 条记录 (<400K)")
        
        # 检查是否达到百万级
        if total_records >= 1000000:
            print("🎉 已达到百万级数据规模！")
        elif total_records >= 400000:
            print("✅ 已达到大规模数据标准")
        else:
            print("⚠️  数据规模偏小，建议检查数据导入")
        
        print("\n💡 推荐测试账号（密码均为password123）：")
        print("-" * 60)
        
        for user_type, samples in user_samples.items():
            if samples and user_type in ['admin', 'teacher', 'student']:
                sample = samples[0]
                username = sample[0]
                name = f"{sample[2]} {sample[3]}".strip() or "未设置"
                print(f"  {user_type.upper():<8}: {username:<15} ({name})")
        
    except Exception as e:
        print(f"❌ 数据验证过程中出错: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()