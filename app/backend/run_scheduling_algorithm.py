#!/usr/bin/env python3
"""
运行排课算法脚本
用于运行排课算法并生成排课结果
"""

import os
import sys
import django
import json
from pathlib import Path

# 添加项目路径（基于脚本位置，提升跨平台兼容性）
BASE_DIR = Path(__file__).resolve().parent  # app/backend
sys.path.insert(0, str(BASE_DIR))

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from apps.schedules.algorithms import create_auto_schedule
from apps.schedules.genetic_algorithm import create_genetic_schedule
from apps.schedules.hybrid_algorithm import create_hybrid_schedule


def make_serializable(obj):
    """将对象转换为可序列化的格式"""
    if isinstance(obj, dict):
        return {str(k): make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # 对于自定义对象，返回其属性字典
        return str(obj)
    else:
        return obj


def run_scheduling_algorithm(algorithm_type="greedy"):
    """运行排课算法"""
    print(f"🧮 开始运行{algorithm_type}排课算法...")
    
    try:
        # 运行指定的算法
        if algorithm_type == "greedy":
            result = create_auto_schedule("2024-1", "2023-2024", algorithm_type="greedy", timeout_seconds=300)
        elif algorithm_type == "genetic":
            result = create_genetic_schedule("2024-1", "2023-2024")
        elif algorithm_type == "hybrid":
            result = create_hybrid_schedule("2024-1", "2023-2024")
        else:
            print(f"❌ 不支持的算法类型: {algorithm_type}")
            return None
        
        print(f"✅ {algorithm_type}算法运行完成")
        print(f"   成功率: {result.get('success_rate', 0):.1f}%")
        print(f"   执行时间: {result.get('execution_time', 0):.2f}秒")
        print(f"   成功分配: {result.get('successful_assignments', 0)}")
        print(f"   总约束数: {result.get('total_constraints', 0)}")
        
        # 清理不能序列化的数据
        if 'algorithm_instance' in result:
            del result['algorithm_instance']
        
        # 处理失败分配的详情
        if 'failed_assignments' in result:
            cleaned_failed = []
            for failed in result['failed_assignments']:
                if isinstance(failed, dict) and 'constraint' in failed:
                    # 移除不能序列化的约束对象
                    failed_copy = failed.copy()
                    del failed_copy['constraint']
                    cleaned_failed.append(failed_copy)
                else:
                    cleaned_failed.append(failed)
            result['failed_assignments'] = cleaned_failed
        
        # 处理分配槽位
        if 'assigned_slots' in result:
            # 将约束对象转换为可序列化的格式
            cleaned_assigned = {}
            for constraint, slots in result['assigned_slots'].items():
                constraint_key = f"{constraint.course.code}-{constraint.teacher.username}"
                cleaned_assigned[constraint_key] = [
                    {
                        'day_of_week': slot.day_of_week,
                        'time_slot': slot.time_slot.name,
                        'classroom': str(slot.classroom)
                    }
                    for slot in slots
                ]
            result['assigned_slots'] = cleaned_assigned
        
        # 保存结果到文件
        output_file = f"scheduling_result_{algorithm_type}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 排课结果已保存到 {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ 运行{algorithm_type}算法时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print("🚀 开始运行排课算法...")
    print("=" * 50)
    
    # 先运行贪心算法（更稳定）
    result = run_scheduling_algorithm("greedy")
    
    if result:
        print()
        print("=" * 50)
        print("🎉 排课算法运行完成!")
        
        # 显示一些关键统计信息
        if 'constraint_stats' in result:
            constraint_stats = result['constraint_stats']
            print(f"📊 约束统计:")
            print(f"   总约束数: {constraint_stats.get('total_constraints', 0)}")
            if 'constraints_by_priority' in constraint_stats:
                print(f"   按优先级分布: {constraint_stats['constraints_by_priority']}")
            if 'constraints_by_type' in constraint_stats:
                print(f"   按类型分布: {constraint_stats['constraints_by_type']}")
        
        if 'resource_utilization' in result:
            resource_stats = result['resource_utilization']
            print(f"📈 资源利用率:")
            if 'classroom_usage' in resource_stats:
                print(f"   教室使用数: {len(resource_stats['classroom_usage'])}")
            if 'teacher_workload' in resource_stats:
                print(f"   教师参与数: {len(resource_stats['teacher_workload'])}")
    else:
        print()
        print("=" * 50)
        print("❌ 排课算法运行失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()