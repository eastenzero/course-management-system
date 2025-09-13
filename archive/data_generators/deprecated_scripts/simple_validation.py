#!/usr/bin/env python3
"""
简化数据库验证脚本
"""

import psycopg2
import time
from datetime import datetime

def validate_database():
    """验证数据库"""
    print("🚀 开始数据库验证")
    print("=" * 60)
    
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
        
        # 核心表统计
        tables = [
            ('users_user', '用户表'),
            ('courses_course', '课程表'),
            ('courses_enrollment', '选课记录表'),
            ('classrooms_classroom', '教室表'),
            ('students_profile', '学生档案表'),
            ('teachers_profile', '教师档案表')
        ]
        
        print(f"\n📊 核心表统计:")
        print("-" * 60)
        
        total_records = 0
        for table_name, table_desc in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                total_records += count
                print(f"   {table_desc:<15} {count:>10,} 条记录")
            except Exception as e:
                print(f"   {table_desc:<15} {'ERROR':>10} ({e})")
        
        print("-" * 60)
        print(f"   {'总计':<15} {total_records:>10,} 条记录")
        
        # 用户类型分布
        print(f"\n👥 用户类型分布:")
        try:
            cursor.execute("""
                SELECT 
                    COALESCE(user_type, 'NULL') as user_type, 
                    COUNT(*) as count 
                FROM users_user 
                GROUP BY user_type 
                ORDER BY count DESC
            """)
            user_types = cursor.fetchall()
            for user_type, count in user_types:
                print(f"   {user_type:<15} {count:>10,} 个用户")
        except Exception as e:
            print(f"   查询失败: {e}")
        
        # 数据质量检查
        print(f"\n🔍 数据质量检查:")
        
        # 检查空值
        try:
            cursor.execute("SELECT COUNT(*) FROM users_user WHERE username IS NULL OR username = ''")
            null_usernames = cursor.fetchone()[0]
            print(f"   空用户名: {null_usernames}")
        except:
            print(f"   空用户名: 检查失败")
        
        # 检查重复
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT username FROM users_user 
                    GROUP BY username HAVING COUNT(*) > 1
                ) duplicates
            """)
            duplicate_usernames = cursor.fetchone()[0]
            print(f"   重复用户名: {duplicate_usernames}")
        except:
            print(f"   重复用户名: 检查失败")
        
        # 性能测试
        print(f"\n⚡ 简单性能测试:")
        
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM users_user")
        user_count = cursor.fetchone()[0]
        query_time = (time.time() - start_time) * 1000
        print(f"   用户计数查询: {query_time:.2f}ms ({user_count:,} 条记录)")
        
        # 生成报告
        print(f"\n📋 验证总结:")
        print("=" * 60)
        print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据库状态: {'✅ 正常' if total_records > 0 else '❌ 异常'}")
        print(f"总记录数: {total_records:,}")
        
        if total_records >= 1000000:
            print("🎉 百万级数据导入成功！可以开始算法测试")
        elif total_records >= 100000:
            print("⚠️ 大规模数据导入部分完成")
        elif total_records > 0:
            print("ℹ️ 有数据，但规模较小")
        else:
            print("❌ 没有数据或导入失败")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    validate_database()