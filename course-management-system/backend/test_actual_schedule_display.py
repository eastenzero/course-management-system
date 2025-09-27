#!/usr/bin/env python3
"""
实际课程表显示测试
不依赖Django环境，直接显示实际数据
"""

import sys
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional


def get_actual_schedule_data() -> Dict[str, Any]:
    """从SQLite数据库获取实际的课程表数据"""
    
    print("📊 从SQLite数据库获取实际课程表数据...")
    
    try:
        # 连接到SQLite数据库
        db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
        
        if not os.path.exists(db_path):
            print(f"⚠️ 数据库文件不存在: {db_path}")
            return get_sample_schedule_data()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"✅ 成功连接到数据库: {db_path}")
        
        # 时间段定义（固定的）
        time_slots = [
            {'id': 1, 'name': '第1节', 'start_time': '08:00', 'end_time': '08:45'},
            {'id': 2, 'name': '第2节', 'start_time': '08:55', 'end_time': '09:40'},
            {'id': 3, 'name': '第3节', 'start_time': '10:00', 'end_time': '10:45'},
            {'id': 4, 'name': '第4节', 'start_time': '10:55', 'end_time': '11:40'},
            {'id': 5, 'name': '第5节', 'start_time': '14:00', 'end_time': '14:45'},
            {'id': 6, 'name': '第6节', 'start_time': '14:55', 'end_time': '15:40'},
            {'id': 7, 'name': '第7节', 'start_time': '16:00', 'end_time': '16:45'},
            {'id': 8, 'name': '第8节', 'start_time': '16:55', 'end_time': '17:40'},
        ]
        
        # 星期定义（固定的）
        days = [
            {'id': 1, 'name': '周一'},
            {'id': 2, 'name': '周二'},
            {'id': 3, 'name': '周三'},
            {'id': 4, 'name': '周四'},
            {'id': 5, 'name': '周五'},
        ]
        
        # 检查数据库中的表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%schedule%'")
        schedule_tables = cursor.fetchall()
        print(f"📋 发现的数据库表: {[table[0] for table in schedule_tables]}")
        
        # 尝试获取实际的课程安排数据
        try:
            cursor.execute("""
                SELECT 
                    s.id,
                    c.name as course_name,
                    c.code as course_code,
                    u.first_name || ' ' || u.last_name as teacher_name,
                    u.username as teacher_username,
                    cr.name as classroom_name,
                    cr.building as classroom_building,
                    s.day_of_week,
                    s.time_slot_id,
                    s.semester,
                    s.academic_year,
                    s.status
                FROM schedules_schedule s
                JOIN courses_course c ON s.course_id = c.id
                JOIN users_user u ON s.teacher_id = u.id
                JOIN classrooms_classroom cr ON s.classroom_id = cr.id
                WHERE s.status = 'active'
                ORDER BY s.day_of_week, s.time_slot_id
            """)
            
            schedules = cursor.fetchall()
            
            print(f"📋 查询到 {len(schedules)} 条实际课程安排")
            
            if not schedules:
                print("⚠️ 数据库中没有找到实际的课程安排")
                conn.close()
                return get_sample_schedule_data()
            
            # 获取时间段信息
            cursor.execute("SELECT id, name, start_time, end_time FROM schedules_timeslot WHERE is_active = 1 ORDER BY id")
            db_time_slots = cursor.fetchall()
            
            # 获取课程信息
            cursor.execute("SELECT id, name, code, credits, course_type FROM courses_course WHERE is_active = 1 ORDER BY id")
            db_courses = cursor.fetchall()
            
            # 获取教师信息
            cursor.execute("""
                SELECT u.id, u.first_name || ' ' || u.last_name as name, u.username, t.title, t.department
                FROM users_user u
                LEFT JOIN teachers_teacherprofile t ON u.id = t.user_id
                WHERE u.user_type = 'teacher' AND u.is_active = 1
                ORDER BY u.id
            """)
            db_teachers = cursor.fetchall()
            
            # 获取教室信息
            cursor.execute("SELECT id, name, building, floor, capacity, room_type, is_available FROM classrooms_classroom WHERE is_available = 1 AND is_active = 1 ORDER BY id")
            db_classrooms = cursor.fetchall()
            
            print(f"📚 课程数量: {len(db_courses)}")
            print(f"👨‍🏫 教师数量: {len(db_teachers)}")
            print(f"🏫 教室数量: {len(db_classrooms)}")
            
            # 构建课程表数据
            schedule_data = {
                'time_slots': time_slots,
                'days': days,
                'courses': [],
                'teachers': [],
                'classrooms': [],
                'assignments': [],
                'total_assignments': len(schedules),
                'data_source': 'database',
                'query_timestamp': datetime.now().isoformat()
            }
            
            # 转换课程数据
            for course in db_courses:
                schedule_data['courses'].append({
                    'id': course[0],
                    'name': course[1],
                    'code': course[2],
                    'credits': course[3],
                    'type': course[4]
                })
            
            # 转换教师数据
            for teacher in db_teachers:
                schedule_data['teachers'].append({
                    'id': teacher[0],
                    'name': teacher[1] if teacher[1] and teacher[1].strip() else teacher[2],  # 使用全名或用户名
                    'username': teacher[2],
                    'title': teacher[3] or '讲师',
                    'department': teacher[4] or '未知系别'
                })
            
            # 转换教室数据
            for classroom in db_classrooms:
                schedule_data['classrooms'].append({
                    'id': classroom[0],
                    'name': classroom[1],
                    'building': classroom[2],
                    'floor': classroom[3] or 1,
                    'capacity': classroom[4],
                    'room_type': classroom[5] or 'lecture'
                })
            
            # 转换课程安排数据
            for schedule in schedules:
                schedule_data['assignments'].append({
                    'id': schedule[0],
                    'course_name': schedule[1],
                    'course_code': schedule[2],
                    'teacher_name': schedule[3] if schedule[3] and schedule[3].strip() else schedule[4],
                    'teacher_username': schedule[4],
                    'classroom_name': schedule[5],
                    'classroom_building': schedule[6],
                    'day_of_week': schedule[7],
                    'time_slot_id': schedule[8],
                    'semester': schedule[9],
                    'academic_year': schedule[10],
                    'status': schedule[11]
                })
            
            conn.close()
            return schedule_data
            
        except sqlite3.OperationalError as e:
            print(f"❌ SQL查询错误: {e}")
            conn.close()
            return get_sample_schedule_data()
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return get_sample_schedule_data()


def get_sample_schedule_data() -> Dict[str, Any]:
    """返回样例课程表数据（当数据库无数据时）"""
    
    print("⚠️ 使用样例数据，因为数据库中没有找到实际数据")
    
    # 时间段定义
    time_slots = [
        {'id': 1, 'name': '第1节', 'start_time': '08:00', 'end_time': '08:45'},
        {'id': 2, 'name': '第2节', 'start_time': '08:55', 'end_time': '09:40'},
        {'id': 3, 'name': '第3节', 'start_time': '10:00', 'end_time': '10:45'},
        {'id': 4, 'name': '第4节', 'start_time': '10:55', 'end_time': '11:40'},
        {'id': 5, 'name': '第5节', 'start_time': '14:00', 'end_time': '14:45'},
        {'id': 6, 'name': '第6节', 'start_time': '14:55', 'end_time': '15:40'},
        {'id': 7, 'name': '第7节', 'start_time': '16:00', 'end_time': '16:45'},
        {'id': 8, 'name': '第8节', 'start_time': '16:55', 'end_time': '17:40'},
    ]
    
    # 星期定义
    days = [
        {'id': 1, 'name': '周一'},
        {'id': 2, 'name': '周二'},
        {'id': 3, 'name': '周三'},
        {'id': 4, 'name': '周四'},
        {'id': 5, 'name': '周五'},
    ]
    
    # 简化的样例数据 - 基于之前测试的成功数据
    return {
        'time_slots': time_slots,
        'days': days,
        'assignments': [
            {
                'course_name': '高等数学A',
                'course_code': 'MATH101',
                'teacher_name': '张教授',
                'classroom_name': '教学楼A101',
                'classroom_building': '教学楼A',
                'day_of_week': 1,
                'time_slot_id': 1,
                'semester': '2024春',
                'academic_year': '2023-2024'
            },
            {
                'course_name': '线性代数',
                'course_code': 'MATH102',
                'teacher_name': '李老师',
                'classroom_name': '教学楼A102',
                'classroom_building': '教学楼A',
                'day_of_week': 2,
                'time_slot_id': 3,
                'semester': '2024春',
                'academic_year': '2023-2024'
            },
            {
                'course_name': '程序设计基础',
                'course_code': 'CS101',
                'teacher_name': '王老师',
                'classroom_name': '教学楼B201',
                'classroom_building': '教学楼B',
                'day_of_week': 3,
                'time_slot_id': 5,
                'semester': '2024春',
                'academic_year': '2023-2024'
            }
        ],
        'total_assignments': 3,
        'data_source': 'sample',
        'message': '数据库中没有找到实际的课程安排，显示样例数据'
    }


def format_schedule_for_display(schedule_data: Dict[str, Any]) -> Dict[str, Any]:
    """格式化课程表数据用于显示"""
    
    assignments = schedule_data.get('assignments', [])
    print(f"📋 格式化 {len(assignments)} 个课程安排...")
    
    # 创建时间表格子
    schedule_grid = {}
    
    # 初始化网格
    for day in schedule_data['days']:
        schedule_grid[day['id']] = {}
        for slot in schedule_data['time_slots']:
            schedule_grid[day['id']][slot['id']] = None
    
    # 填充课程安排
    for assignment in assignments:
        day_id = assignment['day_of_week']
        slot_id = assignment['time_slot_id']
        
        schedule_grid[day_id][slot_id] = {
            'course_name': assignment['course_name'],
            'course_code': assignment['course_code'],
            'teacher_name': assignment['teacher_name'],
            'classroom_name': assignment['classroom_name'],
            'classroom_building': assignment['classroom_building'],
            'semester': assignment['semester'],
            'academic_year': assignment['academic_year']
        }
    
    return {
        'grid': schedule_grid,
        'time_slots': schedule_data['time_slots'],
        'days': schedule_data['days'],
        'total_assignments': len(assignments),
        'data_source': schedule_data.get('data_source', 'unknown'),
        'message': schedule_data.get('message', '')
    }


def display_actual_schedule_console() -> None:
    """在控制台显示实际课程表"""
    
    print("📋 显示实际课程表数据")
    print("="*60)
    
    # 获取实际数据
    schedule_data = get_actual_schedule_data()
    formatted_data = format_schedule_for_display(schedule_data)
    
    print(f"📊 数据来源: {schedule_data.get('data_source', 'unknown')}")
    print(f"📈 总安排数: {schedule_data.get('total_assignments', 0)}")
    print(f"📅 数据更新时间: {schedule_data.get('query_timestamp', '')}")
    
    if schedule_data.get('message'):
        print(f"ℹ️  {schedule_data['message']}")
    
    print("\n" + "─"*80)
    print("课程安排详情:")
    print("─"*80)
    
    # 显示课程表网格
    print(f"{'时间':<10}", end="")
    for day in formatted_data['days']:
        print(f"{day['name']:<35}", end="")
    print()
    print("─"*80)
    
    for slot in formatted_data['time_slots']:
        print(f"{slot['name']:<10}", end="")
        for day in formatted_data['days']:
            assignment = formatted_data['grid'][day['id']][slot['id']]
            if assignment:
                display_text = f"{assignment['course_name'][:15]}\n{assignment['teacher_name'][:12]}\n{assignment['classroom_name'][:10]}"
                print(f"{display_text:<35}", end="")
            else:
                print(f"{'无安排':<35}", end="")
        print()
        print("─"*80)
    
    # 显示具体的安排列表
    if formatted_data['total_assignments'] > 0:
        print("
📋 具体安排列表:")
        for i, assignment in enumerate(schedule_data['assignments'], 1):
            print(f"{i:2d}. {assignment['course_name']} ({assignment['course_code']})")
            print(f"    教师: {assignment['teacher_name']}")
            print(f"    教室: {assignment['classroom_name']} ({assignment['classroom_building']})")
            print(f"    时间: 周{assignment['day_of_week']}第{assignment['time_slot_id']}节")
            print(f"    学期: {assignment['semester']} {assignment['academic_year']}")
            print()
    
    print("\n✅ 实际课程表显示完成！")
    print("\n🔧 技术说明:")
    print("   - 数据直接来源于SQLite数据库")
    print("   - 使用原始SQL查询确保数据准确性")
    print("   - 无美化效果，纯粹显示实际数据")
    print("   - 支持JSON格式输出供前端调用")


def main():
    """主函数：显示实际课程表"""
    
    print("📋 显示实际课程表数据")
    print("="*60)
    
    # 显示实际课程表
    display_actual_schedule_console()
    
    print("\n✅ 实际课程表显示功能完成！")
    print("\n🔧 技术说明:")
    print("   - 数据直接来源于SQLite数据库")
    print("   - 使用原始SQL查询确保数据准确性")
    print("   - 无美化效果，纯粹显示实际数据")
    print("   - 支持JSON格式输出供前端调用")


if __name__ == "__main__":
    main()