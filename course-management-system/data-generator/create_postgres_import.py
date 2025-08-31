#!/usr/bin/env python3
"""
将JSON数据转换为PostgreSQL兼容的SQL导入脚本
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_json_data(json_file_path: str):
    """加载JSON数据"""
    print(f"📂 加载数据文件: {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ 数据文件加载成功")
    return data

def escape_sql_string(value):
    """转义SQL字符串"""
    if value is None:
        return 'NULL'
    if isinstance(value, str):
        # 转义单引号
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    elif isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return f"'{str(value)}'"

def generate_postgres_sql(data, output_file):
    """生成PostgreSQL兼容的SQL文件"""
    print(f"🔧 生成PostgreSQL SQL文件: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- PostgreSQL数据导入脚本\n")
        f.write("-- 生成时间: " + datetime.now().isoformat() + "\n\n")
        
        # 禁用外键检查
        f.write("SET session_replication_role = replica;\n\n")
        
        # 导入用户数据
        print("   👥 生成用户数据SQL...")
        users_sql = []
        students_sql = []
        teachers_sql = []
        
        # 处理学生用户
        for i, student in enumerate(data['students'], 1):
            user_sql = f"""INSERT INTO users_user (id, username, email, first_name, last_name, user_type, is_active, password, date_joined, is_superuser, is_staff) VALUES 
({i}, {escape_sql_string(student['username'])}, {escape_sql_string(student['email'])}, 
{escape_sql_string(student['first_name'])}, {escape_sql_string(student['last_name'])}, 
'student', TRUE, 'pbkdf2_sha256$100000$example$dummyhash', NOW(), FALSE, FALSE);"""
            users_sql.append(user_sql)
            
            # 学生档案
            student_profile_sql = f"""INSERT INTO students_profile (user_id, student_id, major_name, year, phone, address) VALUES 
({i}, {escape_sql_string(student['student_id'])}, {escape_sql_string(student.get('major', '未指定专业'))}, 
{student.get('year', 1)}, {escape_sql_string(student.get('phone', ''))}, {escape_sql_string(student.get('address', ''))});"""
            students_sql.append(student_profile_sql)
        
        # 处理教师用户
        student_count = len(data['students'])
        for i, teacher in enumerate(data['teachers'], student_count + 1):
            user_sql = f"""INSERT INTO users_user (id, username, email, first_name, last_name, user_type, is_active, password, date_joined, is_superuser, is_staff) VALUES 
({i}, {escape_sql_string(teacher['username'])}, {escape_sql_string(teacher['email'])}, 
{escape_sql_string(teacher['first_name'])}, {escape_sql_string(teacher['last_name'])}, 
'teacher', TRUE, 'pbkdf2_sha256$100000$example$dummyhash', NOW(), FALSE, FALSE);"""
            users_sql.append(user_sql)
            
            # 教师档案
            teacher_profile_sql = f"""INSERT INTO teachers_profile (user_id, employee_id, department_name, title, phone, office) VALUES 
({i}, {escape_sql_string(teacher['employee_id'])}, {escape_sql_string(teacher.get('department', '未指定院系'))}, 
{escape_sql_string(teacher.get('title', '讲师'))}, {escape_sql_string(teacher.get('phone', ''))}, {escape_sql_string(teacher.get('office', ''))});"""
            teachers_sql.append(teacher_profile_sql)
        
        # 写入用户SQL
        f.write("-- 插入用户数据\n")
        for sql in users_sql:
            f.write(sql + "\n")
        
        f.write("\n-- 插入学生档案\n")
        for sql in students_sql:
            f.write(sql + "\n")
            
        f.write("\n-- 插入教师档案\n")
        for sql in teachers_sql:
            f.write(sql + "\n")
        
        # 导入课程数据
        print("   📚 生成课程数据SQL...")
        f.write("\n-- 插入课程数据\n")
        for i, course in enumerate(data['courses'], 1):
            course_sql = f"""INSERT INTO courses_course (id, name, code, credits, description, course_type, max_students, semester, is_active) VALUES 
({i}, {escape_sql_string(course['name'])}, {escape_sql_string(course['code'])}, 
{course.get('credits', 3)}, {escape_sql_string(course.get('description', ''))}, 
{escape_sql_string(course.get('type', 'elective'))}, {course.get('max_students', 100)}, 
{escape_sql_string(course.get('semester', '2024-1'))}, TRUE);"""
            f.write(course_sql + "\n")
        
        # 导入选课记录 (只导入前10万条以避免文件过大)
        print("   🎯 生成选课记录SQL (前10万条)...")
        f.write("\n-- 插入选课记录 (前10万条)\n")
        enrollments_to_process = data['enrollments'][:100000]  # 限制为10万条
        
        for i, enrollment in enumerate(enrollments_to_process, 1):
            enrollment_sql = f"""INSERT INTO courses_enrollment (id, student_id, course_id, enrollment_date, status) VALUES 
({i}, {enrollment['student_id']}, {enrollment['course_id']}, 
'{enrollment.get('enrollment_date', '2024-01-01')}', 
{escape_sql_string(enrollment.get('status', 'enrolled'))});"""
            f.write(enrollment_sql + "\n")
        
        # 恢复外键检查
        f.write("\n-- 恢复外键检查\n")
        f.write("SET session_replication_role = DEFAULT;\n")
        
        # 更新序列
        f.write("\n-- 更新序列\n")
        f.write(f"SELECT setval('users_user_id_seq', {len(data['students']) + len(data['teachers'])});\n")
        f.write(f"SELECT setval('courses_course_id_seq', {len(data['courses'])});\n")
        f.write(f"SELECT setval('courses_enrollment_id_seq', {len(enrollments_to_process)});\n")
        
    print(f"✅ PostgreSQL SQL文件生成完成")

def main():
    """主函数"""
    print("🚀 开始生成PostgreSQL导入脚本")
    print("="*80)
    
    # 输入和输出文件
    json_file = "conservative_large_output/json/course_data_20250830_161558.json"
    output_file = "conservative_large_output/postgres_import.sql"
    
    try:
        # 加载数据
        data = load_json_data(json_file)
        
        # 生成SQL
        generate_postgres_sql(data, output_file)
        
        print(f"\n🎉 PostgreSQL导入脚本生成完成！")
        print(f"📁 输出文件: {output_file}")
        print(f"📊 包含内容:")
        print(f"   - 用户: {len(data['students']) + len(data['teachers']):,}")
        print(f"   - 学生档案: {len(data['students']):,}")
        print(f"   - 教师档案: {len(data['teachers']):,}")
        print(f"   - 课程: {len(data['courses']):,}")
        print(f"   - 选课记录: 100,000 (限制导入)")
        
        return True
        
    except Exception as e:
        print(f"❌ 脚本生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ PostgreSQL导入脚本生成成功")
    else:
        print("❌ 脚本生成失败")
        sys.exit(1)