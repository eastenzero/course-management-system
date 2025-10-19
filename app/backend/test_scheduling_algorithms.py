#!/usr/bin/env python
"""
排课算法测试脚本
用于测试和验证排课算法的实现
"""

import os
import sys
import django
from datetime import datetime
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
from apps.schedules.performance_comparison import run_performance_comparison


def test_algorithms():
    """测试所有算法"""
    print("🧪 开始测试排课算法...")
    print("=" * 50)
    
    # 测试参数
    semester = "2024春"
    academic_year = "2023-2024"
    
    # 测试贪心算法
    print("🧠 测试贪心算法...")
    try:
        greedy_result = create_auto_schedule(semester, academic_year, algorithm_type='greedy')
        print(f"  ✅ 贪心算法完成: 成功率 {greedy_result['success_rate']:.1f}%")
    except Exception as e:
        print(f"  ❌ 贪心算法失败: {e}")
    
    # 测试遗传算法
    print("🧬 测试遗传算法...")
    try:
        genetic_result = create_genetic_schedule(semester, academic_year)
        print(f"  ✅ 遗传算法完成: 成功率 {genetic_result['success_rate']:.1f}%")
    except Exception as e:
        print(f"  ❌ 遗传算法失败: {e}")
    
    # 测试混合算法
    print("🔄 测试混合算法...")
    try:
        hybrid_result = create_hybrid_schedule(semester, academic_year)
        print(f"  ✅ 混合算法完成: 成功率 {hybrid_result['success_rate']:.1f}%")
    except Exception as e:
        print(f"  ❌ 混合算法失败: {e}")
    
    print("=" * 50)
    print("✅ 算法测试完成")


def test_performance_comparison():
    """测试性能对比功能"""
    print("📊 开始测试性能对比功能...")
    print("=" * 50)
    
    # 测试参数
    semester = "2024春"
    academic_year = "2023-2024"
    
    try:
        # 运行性能对比
        comparison_results = run_performance_comparison(semester, academic_year, timeout_seconds=60)
        print("  ✅ 性能对比完成")
        
        # 显示结果摘要
        print("\n结果摘要:")
        for algorithm in comparison_results['algorithms']:
            if algorithm['status'] == 'completed':
                print(f"  {algorithm['name']}: 成功率 {algorithm['success_rate']:.1f}%, "
                      f"耗时 {algorithm['execution_time']:.2f}秒")
            else:
                print(f"  {algorithm['name']}: 失败")
                
        # 显示最佳算法
        comparison = comparison_results['comparison']
        if comparison and 'best_overall' in comparison:
            best = comparison['best_overall']
            print(f"\n🏆 综合最佳算法: {best['algorithm']}")
            
    except Exception as e:
        print(f"  ❌ 性能对比失败: {e}")
    
    print("=" * 50)
    print("✅ 性能对比测试完成")


def main():
    """主函数"""
    print("🎓 智能排课算法测试套件")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 运行测试
    test_algorithms()
    print()
    test_performance_comparison()
    
    print()
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 所有测试完成!")


if __name__ == "__main__":
    main()