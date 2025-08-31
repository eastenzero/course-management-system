#!/usr/bin/env python3
"""
从生成的大规模数据中提取测试账号信息
"""

import json
import random

def extract_test_accounts():
    """提取测试账号数据"""
    print("📂 正在提取测试账号数据...")
    
    try:
        with open('conservative_large_output/json/course_data_20250830_161558.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 读取数据文件失败: {e}")
        return None
    
    # 提取学生账号
    students = data.get('students', [])
    teachers = data.get('teachers', [])
    
    print(f"✅ 成功加载数据：{len(students):,} 名学生，{len(teachers):,} 名教师")
    
    # 随机选择一些测试账号
    test_students = random.sample(students, min(10, len(students)))
    test_teachers = random.sample(teachers, min(5, len(teachers)))
    
    return {
        'students': test_students,
        'teachers': test_teachers
    }

def format_account_info(accounts):
    """格式化账号信息"""
    if not accounts:
        return "❌ 无法获取账号数据"
    
    result = []
    result.append("🎓 **学生测试账号**\n")
    result.append("| 用户名 | 学号 | 姓名 | 邮箱 | 专业 | 密码 |")
    result.append("|--------|------|------|------|------|------|")
    
    for student in accounts['students']:
        username = student.get('username', 'N/A')
        student_id = student.get('student_id', 'N/A')
        name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
        if not name:
            name = student.get('name', 'N/A')
        email = student.get('email', 'N/A')
        major = student.get('major', 'N/A')
        
        result.append(f"| {username} | {student_id} | {name} | {email} | {major} | password123 |")
    
    result.append("\n👨‍🏫 **教师测试账号**\n")
    result.append("| 用户名 | 工号 | 姓名 | 邮箱 | 院系 | 职称 | 密码 |")
    result.append("|--------|------|------|------|------|------|------|")
    
    for teacher in accounts['teachers']:
        username = teacher.get('username', 'N/A')
        employee_id = teacher.get('employee_id', 'N/A')
        name = f"{teacher.get('first_name', '')} {teacher.get('last_name', '')}".strip()
        if not name:
            name = teacher.get('name', 'N/A')
        email = teacher.get('email', 'N/A')
        department = teacher.get('department', 'N/A')
        title = teacher.get('title', 'N/A')
        
        result.append(f"| {username} | {employee_id} | {name} | {email} | {department} | {title} | password123 |")
    
    result.append(f"\n📋 **管理员测试账号**\n")
    result.append("| 用户名 | 密码 | 角色 | 说明 |")
    result.append("|--------|------|------|------|")
    result.append("| admin | admin123 | 系统管理员 | 具有所有权限 |")
    result.append("| academic_admin | academic123 | 教务管理员 | 课程和选课管理权限 |")
    
    result.append(f"\n🔑 **登录说明**\n")
    result.append("- 默认密码：password123（学生和教师）")
    result.append("- 登录地址：http://localhost:18081")
    result.append("- API地址：http://localhost:18000/api")
    result.append("- 所有账号均为生成的测试数据")
    result.append("- 账号已包含在生成的458,782条记录中")
    
    return "\n".join(result)

def main():
    """主函数"""
    print("🚀 开始提取测试账号")
    print("="*60)
    
    accounts = extract_test_accounts()
    account_info = format_account_info(accounts)
    
    # 保存账号信息到文件
    with open('test_accounts.md', 'w', encoding='utf-8') as f:
        f.write("# 测试账号数据\n\n")
        f.write("**生成时间**: 2025-08-30 16:15\n")
        f.write("**数据来源**: conservative_large_output (458,782条记录)\n\n")
        f.write(account_info)
    
    print(account_info)
    print(f"\n✅ 测试账号信息已保存到: test_accounts.md")

if __name__ == "__main__":
    main()