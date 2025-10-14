#!/usr/bin/env python3
"""
独立版：将算法生成的排课结果转换为前端可用的JSON格式
不依赖Django环境
"""

import json
import os
from datetime import datetime
from pathlib import Path

def convert_schedule_data():
    """转换排课数据为前端可用格式"""
    print("开始转换排课数据...")
    
    try:
        # 基于脚本位置构建路径，提升跨平台兼容性
        backend_dir = Path(__file__).resolve().parent
        app_root = backend_dir.parent
        algorithms_result = app_root / 'algorithms' / 'genetic_scheduling_result.json'
        frontend_public_data = app_root / 'frontend' / 'public' / 'data' / 'schedules.json'
        backup_path = backend_dir / 'schedule_data.json'

        # 加载算法生成的排课结果
        try:
            with open(algorithms_result, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
        except FileNotFoundError:
            print("未找到算法排课结果文件")
            return False
        
        assignments = result_data.get('assignments', [])
        if not assignments:
            print("排课结果中没有分配数据")
            return False
        
        print(f"准备转换 {len(assignments)} 条排课记录")
        
        # 转换数据格式为前端可用格式
        schedules = []
        
        # 模拟课程、教师、教室数据（基于算法生成的ID映射）
        course_names = {
            1: "高等数学A", 2: "线性代数", 3: "概率论与数理统计", 
            4: "离散数学", 5: "数据结构", 6: "算法设计",
            7: "计算机组成原理", 8: "操作系统", 9: "计算机网络",
            10: "数据库系统", 11: "软件工程", 12: "编译原理"
        }
        
        teacher_names = {
            1: "张教授", 2: "李教授", 3: "王教授", 4: "陈教授",
            5: "刘教授", 6: "赵教授", 7: "孙教授", 8: "周教授",
            9: "吴教授", 10: "郑教授"
        }
        
        classroom_names = {
            1: "A101", 2: "A102", 3: "A103", 4: "A104", 5: "A201",
            6: "A202", 7: "A203", 8: "A204", 9: "B101", 10: "B102",
            11: "B103", 12: "B104"
        }
        
        day_names = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五", 6: "周六", 7: "周日"}
        
        time_slot_mapping = {
            1: "08:00-09:40", 2: "10:00-11:40", 3: "14:00-15:40",
            4: "16:00-17:40", 5: "19:00-20:40", 6: "08:00-09:40",
            7: "10:00-11:40", 8: "14:00-15:40", 9: "16:00-17:40"
        }
        
        for i, assignment in enumerate(assignments):
            course_id = assignment.get('course_id', 1)
            teacher_id = assignment.get('teacher_id', 1)
            classroom_id = assignment.get('classroom_id', 1)
            day_of_week = assignment.get('day_of_week', 1)
            time_slot = assignment.get('time_slot', 1)
            
            schedule = {
                "id": str(i + 1),
                "courseCode": f"COURSE{course_id:03d}",
                "courseName": course_names.get(course_id, f"课程{course_id}"),
                "teacher": teacher_names.get(teacher_id, f"教师{teacher_id}"),
                "classroom": classroom_names.get(classroom_id, f"教室{classroom_id}"),
                "dayOfWeek": day_of_week,
                "startTime": time_slot_mapping.get(time_slot, "10:00-11:40").split("-")[0],
                "endTime": time_slot_mapping.get(time_slot, "10:00-11:40").split("-")[1],
                "weeks": assignment.get('week_range', '1-16'),
                "semester": assignment.get('semester', '2024春')
            }
            schedules.append(schedule)
        
        # 保存转换后的数据
        output_data = {
            "schedules": schedules,
            "total": len(schedules),
            "semester": "2024春",
            "generated_at": datetime.now().isoformat()
        }
        
        # 保存到前端可访问的位置
        output_path = str(frontend_public_data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功转换 {len(schedules)} 条排课记录")
        print(f"📁 数据已保存到: {output_path}")
        
        # 同时保存一个备份
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 备份数据已保存到: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"转换数据时出错: {e}")
        return False

if __name__ == "__main__":
    success = convert_schedule_data()
    if success:
        print("\n🎉 排课数据转换完成！")
        print("现在可以启动前端服务来查看课程表了。")
    else:
        print("\n❌ 排课数据转换失败！")