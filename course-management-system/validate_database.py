#!/usr/bin/env python3
"""
数据库数据验证脚本
"""

import psycopg2
import time
from datetime import datetime

class DatabaseValidator:
    """数据库验证器"""
    
    def __init__(self):
        self.connection = None
        
    def connect_database(self):
        """连接数据库"""
        try:
            self.connection = psycopg2.connect(
                host="localhost",
                port="15432",
                database="course_management",
                user="postgres",
                password="postgres123"
            )
            print("✅ 数据库连接成功")
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def get_table_statistics(self):
        """获取表统计信息"""
        print("\n📊 数据库表统计:")
        print("-" * 60)
        
        try:
            cursor = self.connection.cursor()
            
            # 获取所有表的记录数
            cursor.execute("""
                SELECT 
                    table_name,
                    (xpath('//row/c/text()', query_to_xml(
                        format('SELECT COUNT(*) as c FROM %I.%I', 
                               table_schema, table_name), 
                        false, true, '')))[1]::text::int as row_count
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            
            tables = cursor.fetchall()
            total_records = 0
            
            for table in tables:
                schema, table_name, inserts, updates, deletes, live_tuples = table
                total_records += live_tuples
                print(f"   {table_name:<30} {live_tuples:>10,} 条记录")
            
            print("-" * 60)
            print(f"   {'总计':<30} {total_records:>10,} 条记录")
            
            return total_records
            
        except Exception as e:
            print(f"❌ 获取表统计失败: {e}")
            return 0
    
    def validate_data_integrity(self):
        """验证数据完整性"""
        print("\n🔍 数据完整性验证:")
        print("-" * 60)
        
        try:
            cursor = self.connection.cursor()
            
            # 检查用户数据
            cursor.execute("SELECT COUNT(*) FROM users_user WHERE user_type = 'student'")
            student_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users_user WHERE user_type = 'teacher'")
            teacher_count = cursor.fetchone()[0]
            
            print(f"   学生用户: {student_count:,}")
            print(f"   教师用户: {teacher_count:,}")
            
            # 检查课程数据
            cursor.execute("SELECT COUNT(*) FROM courses_course")
            course_count = cursor.fetchone()[0]
            print(f"   课程数量: {course_count:,}")
            
            # 检查选课记录
            cursor.execute("SELECT COUNT(*) FROM courses_enrollment")
            enrollment_count = cursor.fetchone()[0]
            print(f"   选课记录: {enrollment_count:,}")
            
            # 检查教室数据
            cursor.execute("SELECT COUNT(*) FROM classrooms_classroom")
            classroom_count = cursor.fetchone()[0]
            print(f"   教室数量: {classroom_count:,}")
            
            # 检查档案数据
            cursor.execute("SELECT COUNT(*) FROM students_profile")
            student_profile_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM teachers_profile")
            teacher_profile_count = cursor.fetchone()[0]
            
            print(f"   学生档案: {student_profile_count:,}")
            print(f"   教师档案: {teacher_profile_count:,}")
            
            return {
                'students': student_count,
                'teachers': teacher_count,
                'courses': course_count,
                'enrollments': enrollment_count,
                'classrooms': classroom_count,
                'student_profiles': student_profile_count,
                'teacher_profiles': teacher_profile_count
            }
            
        except Exception as e:
            print(f"❌ 数据完整性验证失败: {e}")
            return {}
    
    def validate_data_quality(self):
        """验证数据质量"""
        print("\n🎯 数据质量验证:")
        print("-" * 60)
        
        try:
            cursor = self.connection.cursor()
            
            # 检查空值
            cursor.execute("""
                SELECT COUNT(*) FROM users_user 
                WHERE username IS NULL OR email IS NULL
            """)
            null_users = cursor.fetchone()[0]
            print(f"   空用户名或邮箱: {null_users}")
            
            # 检查重复用户名
            cursor.execute("""
                SELECT username, COUNT(*) 
                FROM users_user 
                GROUP BY username 
                HAVING COUNT(*) > 1
            """)
            duplicate_users = cursor.fetchall()
            print(f"   重复用户名: {len(duplicate_users)}")
            
            # 检查孤立记录
            cursor.execute("""
                SELECT COUNT(*) FROM courses_course 
                WHERE teacher_id IS NOT NULL 
                AND teacher_id NOT IN (SELECT id FROM users_user WHERE user_type = 'teacher')
            """)
            orphan_courses = cursor.fetchone()[0]
            print(f"   孤立课程: {orphan_courses}")
            
            # 检查数据分布
            cursor.execute("""
                SELECT user_type, COUNT(*) 
                FROM users_user 
                GROUP BY user_type
            """)
            user_distribution = cursor.fetchall()
            print("   用户类型分布:")
            for user_type, count in user_distribution:
                print(f"     {user_type}: {count:,}")
            
        except Exception as e:
            print(f"❌ 数据质量验证失败: {e}")
    
    def performance_test(self):
        """性能测试"""
        print("\n⚡ 性能测试:")
        print("-" * 60)
        
        try:
            cursor = self.connection.cursor()
            
            # 测试查询性能
            queries = [
                ("用户查询", "SELECT COUNT(*) FROM users_user"),
                ("课程查询", "SELECT COUNT(*) FROM courses_course"),
                ("选课记录查询", "SELECT COUNT(*) FROM courses_enrollment"),
                ("复杂连接查询", """
                    SELECT COUNT(*) 
                    FROM users_user u 
                    JOIN courses_enrollment e ON u.id = e.student_id 
                    JOIN courses_course c ON e.course_id = c.id
                """)
            ]
            
            for query_name, query in queries:
                start_time = time.time()
                cursor.execute(query)
                result = cursor.fetchone()[0]
                end_time = time.time()
                
                duration = (end_time - start_time) * 1000  # 毫秒
                print(f"   {query_name:<20} {duration:>8.2f}ms ({result:,} 条记录)")
                
        except Exception as e:
            print(f"❌ 性能测试失败: {e}")
    
    def generate_summary_report(self, stats):
        """生成总结报告"""
        print("\n📋 数据导入总结报告")
        print("=" * 80)
        
        total_records = sum(stats.values()) if stats else 0
        
        print(f"导入时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总记录数: {total_records:,}")
        print(f"数据库状态: {'✅ 正常' if total_records > 0 else '❌ 异常'}")
        
        if stats:
            print("\n详细统计:")
            for key, value in stats.items():
                print(f"  {key}: {value:,}")
        
        # 建议和下一步
        print("\n🎯 建议和下一步操作:")
        if total_records >= 1000000:
            print("✅ 百万级数据导入成功完成")
            print("✅ 可以开始进行智能排课算法测试")
            print("✅ 可以进行系统性能压力测试")
        elif total_records >= 100000:
            print("⚠️ 数据导入部分完成，建议补充剩余数据")
        else:
            print("❌ 数据导入未达到预期，需要重新导入")
        
        print("📚 推荐测试场景:")
        print("  1. 智能排课算法验证")
        print("  2. 大规模选课冲突检测")
        print("  3. 系统响应时间测试")
        print("  4. 数据库查询优化")
        
        print("=" * 80)
    
    def run_full_validation(self):
        """运行完整验证"""
        print("🚀 开始数据库验证流程")
        print("=" * 80)
        
        if not self.connect_database():
            return False
        
        # 获取统计信息
        total_records = self.get_table_statistics()
        
        # 验证数据完整性
        stats = self.validate_data_integrity()
        
        # 验证数据质量
        self.validate_data_quality()
        
        # 性能测试
        self.performance_test()
        
        # 生成总结报告
        self.generate_summary_report(stats)
        
        return True
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()


def main():
    """主函数"""
    validator = DatabaseValidator()
    try:
        validator.run_full_validation()
    finally:
        validator.close()


if __name__ == "__main__":
    main()