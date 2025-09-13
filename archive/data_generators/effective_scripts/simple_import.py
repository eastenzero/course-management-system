#!/usr/bin/env python3
"""
简化的数据导入脚本 - 直接使用SQL
"""

import json
import psycopg2
import time
from pathlib import Path

class SQLDataImporter:
    """SQL数据导入器"""
    
    def __init__(self, data_file: str):
        self.data_file = data_file
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
    
    def load_data(self):
        """加载数据文件"""
        print(f"📂 加载数据文件: {self.data_file}")
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print("✅ 数据文件加载成功")
            return data
        except Exception as e:
            print(f"❌ 数据文件加载失败: {e}")
            return None
    
    def clear_tables(self):
        """清理现有数据"""
        print("🧹 清理现有数据...")
        
        try:
            cursor = self.connection.cursor()
            
            # 禁用外键约束
            cursor.execute("SET session_replication_role = replica;")
            
            # 清理表数据（按依赖关系顺序）
            tables_to_clear = [
                'apps_courses_enrollment',
                'apps_courses_course', 
                'apps_students_student',
                'apps_teachers_teacher',
                'apps_classrooms_classroom',
                'auth_user'
            ]
            
            for table in tables_to_clear:
                try:
                    cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
                    print(f"   清理表: {table}")
                except Exception as e:
                    print(f"   ⚠️ 清理表 {table} 失败: {e}")
            
            # 重新启用外键约束
            cursor.execute("SET session_replication_role = DEFAULT;")
            
            self.connection.commit()
            print("✅ 数据清理完成")
            
        except Exception as e:
            print(f"❌ 数据清理失败: {e}")
            self.connection.rollback()
    
    def create_users(self, students_data, teachers_data):
        """创建用户数据"""
        print(f"👥 创建用户数据...")
        
        try:
            cursor = self.connection.cursor()
            
            # 准备插入语句
            user_insert_sql = """
                INSERT INTO auth_user (
                    username, email, first_name, last_name, 
                    is_staff, is_active, is_superuser, 
                    date_joined, password
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                ON CONFLICT (username) DO NOTHING;
            """
            
            users_data = []
            
            # 准备学生用户数据
            for student in students_data:
                username = f"student_{student['student_id']}"
                email = student.get('email', f"{username}@university.edu")
                name_parts = student['name'].split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                users_data.append((
                    username, email, first_name, last_name,
                    False, True, False, 'pbkdf2_sha256$600000$dummy$dummy'
                ))
            
            # 准备教师用户数据
            for teacher in teachers_data:
                username = f"teacher_{teacher['teacher_id']}"
                email = teacher.get('email', f"{username}@university.edu")
                name_parts = teacher['name'].split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                users_data.append((
                    username, email, first_name, last_name,
                    False, True, False, 'pbkdf2_sha256$600000$dummy$dummy'
                ))
            
            # 批量插入用户
            print(f"   💾 插入 {len(users_data):,} 个用户...")
            cursor.executemany(user_insert_sql, users_data)
            
            self.connection.commit()
            print(f"✅ 用户创建完成")
            
        except Exception as e:
            print(f"❌ 用户创建失败: {e}")
            self.connection.rollback()
            raise
    
    def get_table_info(self):
        """获取表信息"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print("📊 数据库表列表:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   {table[0]}: {count:,} 条记录")
            
        except Exception as e:
            print(f"❌ 获取表信息失败: {e}")
    
    def simple_import(self):
        """简化的导入流程"""
        print("🚀 开始简化数据导入流程")
        print("=" * 60)
        
        start_time = time.time()
        
        # 连接数据库
        if not self.connect_database():
            return False
        
        # 获取表信息
        self.get_table_info()
        
        # 加载数据
        data = self.load_data()
        if not data:
            return False
        
        # 清理现有数据
        self.clear_tables()
        
        # 创建用户
        self.create_users(data.get('students', []), data.get('teachers', []))
        
        # 获取最终统计
        self.get_table_info()
        
        total_time = time.time() - start_time
        print(f"\n🎉 导入完成！总耗时: {total_time:.2f} 秒")
        
        return True
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='简化数据导入器')
    parser.add_argument('--data-file', default='course_dataset.json', help='数据文件路径')
    
    args = parser.parse_args()
    
    importer = SQLDataImporter(args.data_file)
    try:
        success = importer.simple_import()
        if success:
            print("✅ 导入成功完成")
        else:
            print("❌ 导入失败")
    finally:
        importer.close()


if __name__ == "__main__":
    main()