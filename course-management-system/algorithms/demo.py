# file: algorithms/demo.py
# 功能: 智能排课算法演示脚本

import sys
import os
import time
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from engine import SchedulingEngine, AlgorithmType
from models import Assignment, TeacherPreference

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_sample_data():
    """创建示例数据"""
    
    # 课程数据
    courses = [
        {
            'id': 1,
            'name': '高等数学',
            'code': 'MATH101',
            'credits': 4,
            'max_students': 120,
            'course_type': 'required',
            'semester': '2024春',
            'academic_year': '2023-2024',
            'is_active': True,
            'is_published': True,
        },
        {
            'id': 2,
            'name': '线性代数',
            'code': 'MATH102',
            'credits': 3,
            'max_students': 80,
            'course_type': 'required',
            'semester': '2024春',
            'academic_year': '2023-2024',
            'is_active': True,
            'is_published': True,
        },
        {
            'id': 3,
            'name': '计算机程序设计',
            'code': 'CS101',
            'credits': 4,
            'max_students': 60,
            'course_type': 'professional',
            'semester': '2024春',
            'academic_year': '2023-2024',
            'is_active': True,
            'is_published': True,
        },
        {
            'id': 4,
            'name': '数据结构',
            'code': 'CS201',
            'credits': 3,
            'max_students': 50,
            'course_type': 'professional',
            'semester': '2024春',
            'academic_year': '2023-2024',
            'is_active': True,
            'is_published': True,
        },
        {
            'id': 5,
            'name': '大学英语',
            'code': 'ENG101',
            'credits': 2,
            'max_students': 40,
            'course_type': 'public',
            'semester': '2024春',
            'academic_year': '2023-2024',
            'is_active': True,
            'is_published': True,
        },
    ]
    
    # 教师数据
    teachers = [
        {
            'id': 1,
            'name': '张教授',
            'department': '数学系',
            'max_weekly_hours': 16,
            'max_daily_hours': 6,
            'qualified_courses': [1, 2],  # 高等数学、线性代数
        },
        {
            'id': 2,
            'name': '李老师',
            'department': '计算机系',
            'max_weekly_hours': 18,
            'max_daily_hours': 8,
            'qualified_courses': [3, 4],  # 程序设计、数据结构
        },
        {
            'id': 3,
            'name': '王老师',
            'department': '外语系',
            'max_weekly_hours': 20,
            'max_daily_hours': 6,
            'qualified_courses': [5],  # 大学英语
        },
        {
            'id': 4,
            'name': '赵副教授',
            'department': '数学系',
            'max_weekly_hours': 14,
            'max_daily_hours': 6,
            'qualified_courses': [1, 2],  # 高等数学、线性代数
        },
        {
            'id': 5,
            'name': '陈老师',
            'department': '计算机系',
            'max_weekly_hours': 16,
            'max_daily_hours': 8,
            'qualified_courses': [3, 4],  # 程序设计、数据结构
        },
    ]
    
    # 教室数据
    classrooms = [
        {
            'id': 1,
            'name': '教学楼A101',
            'building': '教学楼A',
            'floor': 1,
            'capacity': 150,
            'room_type': 'lecture',
            'equipment': ['投影仪', '音响'],
            'is_available': True,
            'is_active': True,
        },
        {
            'id': 2,
            'name': '教学楼A102',
            'building': '教学楼A',
            'floor': 1,
            'capacity': 100,
            'room_type': 'lecture',
            'equipment': ['投影仪'],
            'is_available': True,
            'is_active': True,
        },
        {
            'id': 3,
            'name': '实验楼B201',
            'building': '实验楼B',
            'floor': 2,
            'capacity': 80,
            'room_type': 'computer',
            'equipment': ['计算机', '投影仪'],
            'is_available': True,
            'is_active': True,
        },
        {
            'id': 4,
            'name': '教学楼C301',
            'building': '教学楼C',
            'floor': 3,
            'capacity': 60,
            'room_type': 'seminar',
            'equipment': ['白板', '投影仪'],
            'is_available': True,
            'is_active': True,
        },
        {
            'id': 5,
            'name': '教学楼A201',
            'building': '教学楼A',
            'floor': 2,
            'capacity': 120,
            'room_type': 'lecture',
            'equipment': ['投影仪', '音响'],
            'is_available': True,
            'is_active': True,
        },
    ]
    
    # 教师偏好数据
    teacher_preferences = [
        TeacherPreference(1, 1, 2, 0.9, True, "偏好周一上午"),  # 张教授
        TeacherPreference(1, 1, 3, 0.8, True, ""),
        TeacherPreference(1, 3, 2, 0.7, True, ""),
        TeacherPreference(2, 2, 1, 0.9, True, "偏好周二第一节"),  # 李老师
        TeacherPreference(2, 2, 2, 0.8, True, ""),
        TeacherPreference(2, 4, 3, 0.7, True, ""),
        TeacherPreference(3, 1, 1, 0.8, True, ""),  # 王老师
        TeacherPreference(3, 3, 1, 0.9, True, "偏好周三第一节"),
        TeacherPreference(3, 5, 2, 0.7, True, ""),
    ]
    
    return courses, teachers, classrooms, teacher_preferences


def demo_greedy_algorithm():
    """演示贪心算法"""
    print("\n" + "="*50)
    print("贪心算法演示")
    print("="*50)
    
    courses, teachers, classrooms, teacher_preferences = create_sample_data()
    
    # 初始化排课引擎
    engine = SchedulingEngine(
        default_algorithm=AlgorithmType.GREEDY,
        enable_conflict_resolution=True,
        enable_optimization=False
    )
    
    engine.initialize(courses, teachers, classrooms, teacher_preferences)
    
    # 生成排课方案
    start_time = time.time()
    result = engine.generate_schedule()
    end_time = time.time()
    
    # 输出结果
    print(f"算法: {result.algorithm_used}")
    print(f"生成时间: {end_time - start_time:.2f} 秒")
    print(f"适应度评分: {result.fitness_score:.2f}")
    print(f"总分配数: {result.total_assignments}")
    print(f"冲突数: {result.conflict_count}")
    print(f"方案有效性: {'有效' if result.is_valid else '无效'}")
    
    # 显示部分分配
    print("\n前5个分配:")
    for i, assignment in enumerate(result.assignments[:5]):
        course_name = next(c['name'] for c in courses if c['id'] == assignment.course_id)
        teacher_name = next(t['name'] for t in teachers if t['id'] == assignment.teacher_id)
        classroom_name = next(c['name'] for c in classrooms if c['id'] == assignment.classroom_id)
        day_names = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        print(f"  {i+1}. {course_name} - {teacher_name} - {classroom_name} - "
              f"{day_names[assignment.day_of_week]} 第{assignment.time_slot}节")
    
    # 显示冲突
    if result.conflicts:
        print(f"\n冲突详情:")
        for i, conflict in enumerate(result.conflicts[:3]):
            print(f"  {i+1}. {conflict.conflict_type}: {conflict.description}")
    
    return result


def demo_genetic_algorithm():
    """演示遗传算法"""
    print("\n" + "="*50)
    print("遗传算法演示")
    print("="*50)
    
    courses, teachers, classrooms, teacher_preferences = create_sample_data()
    
    # 初始化排课引擎
    engine = SchedulingEngine(
        default_algorithm=AlgorithmType.GENETIC,
        enable_conflict_resolution=True,
        enable_optimization=False
    )
    
    engine.initialize(courses, teachers, classrooms, teacher_preferences)
    
    # 配置遗传算法参数
    algorithm_params = {
        'population_size': 50,
        'max_generations': 100,
        'mutation_rate': 0.1,
        'crossover_rate': 0.8,
        'convergence_threshold': 20,
    }
    
    # 生成排课方案
    start_time = time.time()
    result = engine.generate_schedule(
        algorithm=AlgorithmType.GENETIC,
        algorithm_params=algorithm_params
    )
    end_time = time.time()
    
    # 输出结果
    print(f"算法: {result.algorithm_used}")
    print(f"生成时间: {end_time - start_time:.2f} 秒")
    print(f"适应度评分: {result.fitness_score:.2f}")
    print(f"总分配数: {result.total_assignments}")
    print(f"冲突数: {result.conflict_count}")
    print(f"方案有效性: {'有效' if result.is_valid else '无效'}")
    
    return result


def demo_hybrid_algorithm():
    """演示混合算法"""
    print("\n" + "="*50)
    print("混合算法演示")
    print("="*50)
    
    courses, teachers, classrooms, teacher_preferences = create_sample_data()
    
    # 初始化排课引擎
    engine = SchedulingEngine(
        default_algorithm=AlgorithmType.HYBRID,
        enable_conflict_resolution=True,
        enable_optimization=True
    )
    
    engine.initialize(courses, teachers, classrooms, teacher_preferences)
    
    # 生成排课方案
    start_time = time.time()
    result = engine.generate_schedule()
    end_time = time.time()
    
    # 输出结果
    print(f"算法: {result.algorithm_used}")
    print(f"生成时间: {end_time - start_time:.2f} 秒")
    print(f"适应度评分: {result.fitness_score:.2f}")
    print(f"总分配数: {result.total_assignments}")
    print(f"冲突数: {result.conflict_count}")
    print(f"方案有效性: {'有效' if result.is_valid else '无效'}")
    
    # 显示算法统计
    stats = engine.get_statistics()
    print(f"\n引擎统计:")
    print(f"  成功生成: {stats['engine_stats']['successful_schedules']}")
    print(f"  失败生成: {stats['engine_stats']['failed_schedules']}")
    print(f"  平均生成时间: {stats['engine_stats']['average_generation_time']:.2f} 秒")
    
    return result


def demo_schedule_analysis():
    """演示排课分析"""
    print("\n" + "="*50)
    print("排课分析演示")
    print("="*50)
    
    # 先生成一个排课方案
    courses, teachers, classrooms, teacher_preferences = create_sample_data()
    
    engine = SchedulingEngine()
    engine.initialize(courses, teachers, classrooms, teacher_preferences)
    
    result = engine.generate_schedule(algorithm=AlgorithmType.GREEDY)
    
    # 分析排课方案
    analysis = engine.analyze_schedule(result)
    
    print("排课分析结果:")
    print(f"  总分配数: {analysis['schedule_summary']['total_assignments']}")
    print(f"  适应度评分: {analysis['schedule_summary']['fitness_score']:.2f}")
    print(f"  冲突数: {analysis['schedule_summary']['conflicts']}")
    print(f"  方案有效性: {'有效' if analysis['schedule_summary']['is_valid'] else '无效'}")
    
    # 资源利用率分析
    resource_analysis = analysis['resource_analysis']
    print(f"\n资源利用率:")
    print(f"  教师平均负荷: {resource_analysis['teacher_utilization']['average_load']:.1f} 课时")
    print(f"  教室平均使用: {resource_analysis['classroom_utilization']['average_usage']:.1f} 次")
    print(f"  使用时间段数: {resource_analysis['time_utilization']['total_time_slots_used']}")
    
    return analysis


def main():
    """主函数"""
    print("智能排课算法演示系统")
    print("="*50)
    
    try:
        # 演示不同算法
        greedy_result = demo_greedy_algorithm()
        genetic_result = demo_genetic_algorithm()
        hybrid_result = demo_hybrid_algorithm()
        
        # 演示分析功能
        analysis = demo_schedule_analysis()
        
        # 比较结果
        print("\n" + "="*50)
        print("算法比较")
        print("="*50)
        
        results = [
            ("贪心算法", greedy_result),
            ("遗传算法", genetic_result),
            ("混合算法", hybrid_result),
        ]
        
        print(f"{'算法':<12} {'适应度':<10} {'冲突数':<8} {'有效性':<8}")
        print("-" * 40)
        
        for name, result in results:
            validity = "有效" if result.is_valid else "无效"
            print(f"{name:<12} {result.fitness_score:<10.2f} {result.conflict_count:<8} {validity:<8}")
        
        print("\n演示完成！")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
