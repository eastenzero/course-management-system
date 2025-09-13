#!/usr/bin/env python
"""
课程表验证工具 - 验证排课结果的合理性
提供可视化验证和质量分析功能
"""

import os
import sys
import django
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict, Counter

# 设置Django环境
# 添加backend路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment

# 添加算法模块路径
sys.path.append('algorithms')
from engine import SchedulingEngine, AlgorithmType

User = get_user_model()

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


class ScheduleValidator:
    """课程表验证器"""
    
    def __init__(self):
        self.time_slots = {
            1: "08:00-08:45", 2: "08:55-09:40", 3: "09:50-10:35", 4: "10:45-11:30",
            5: "13:30-14:15", 6: "14:25-15:10", 7: "15:20-16:05", 8: "16:15-17:00",
            9: "18:30-19:15", 10: "19:25-20:10"
        }
        
        self.weekdays = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五"}
        
    def run_algorithm_test(self, algorithm_type: str = 'hybrid') -> Dict[str, Any]:
        """运行算法测试"""
        print(f"🎯 运行 {algorithm_type} 算法测试...")
        
        # 获取测试数据
        teachers = self._get_test_teachers()
        courses = self._get_test_courses()
        classrooms = self._get_test_classrooms()
        
        if not teachers or not courses:
            print("❌ 没有找到测试数据，请先运行 smart_data_generator.py")
            return {}
        
        print(f"   📊 数据规模: {len(teachers)} 教师, {len(courses)} 课程, {len(classrooms)} 教室")
        
        # 初始化排课引擎
        engine = SchedulingEngine()
        engine.initialize(courses, teachers, classrooms)
        
        # 选择算法类型
        algorithm_map = {
            'greedy': AlgorithmType.GREEDY,
            'genetic': AlgorithmType.GENETIC,
            'hybrid': AlgorithmType.HYBRID
        }
        
        algorithm = algorithm_map.get(algorithm_type, AlgorithmType.HYBRID)
        
        # 生成排课方案
        print(f"   🔄 正在运行 {algorithm_type} 算法...")
        result = engine.generate_schedule(algorithm=algorithm)
        
        # 分析结果
        analysis = engine.analyze_schedule(result)
        
        print(f"   ✅ 算法完成: 适应度={result.fitness_score:.2f}, 冲突={len(result.conflicts)}")
        
        return {
            'result': result,
            'analysis': analysis,
            'engine': engine
        }
    
    def validate_schedule_quality(self, result) -> Dict[str, Any]:
        """验证课程表质量"""
        print("📋 验证课程表质量...")
        
        if not result.assignments:
            return {'error': '没有排课结果可验证'}
        
        # 基础统计
        total_assignments = len(result.assignments)
        conflicts = len(result.conflicts)
        
        # 时间分布分析
        time_distribution = self._analyze_time_distribution(result.assignments)
        
        # 教师负载分析
        teacher_load = self._analyze_teacher_load(result.assignments)
        
        # 教室利用率分析
        classroom_usage = self._analyze_classroom_usage(result.assignments)
        
        # 课程分布分析
        course_distribution = self._analyze_course_distribution(result.assignments)
        
        quality_score = self._calculate_quality_score(
            conflicts, total_assignments, time_distribution, teacher_load
        )
        
        return {
            'basic_stats': {
                'total_assignments': total_assignments,
                'conflicts': conflicts,
                'conflict_rate': conflicts / total_assignments if total_assignments > 0 else 0,
                'fitness_score': result.fitness_score,
                'quality_score': quality_score
            },
            'time_distribution': time_distribution,
            'teacher_load': teacher_load,
            'classroom_usage': classroom_usage,
            'course_distribution': course_distribution
        }
    
    def generate_visual_report(self, validation_data: Dict, save_path: str = None) -> str:
        """生成可视化报告"""
        print("📊 生成可视化报告...")
        
        if 'error' in validation_data:
            return f"无法生成报告: {validation_data['error']}"
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('课程表质量分析报告', fontsize=16, fontweight='bold')
        
        # 1. 时间分布热力图
        self._plot_time_heatmap(axes[0, 0], validation_data['time_distribution'])
        
        # 2. 教师负载分布
        self._plot_teacher_load(axes[0, 1], validation_data['teacher_load'])
        
        # 3. 教室利用率
        self._plot_classroom_usage(axes[1, 0], validation_data['classroom_usage'])
        
        # 4. 质量指标雷达图
        self._plot_quality_radar(axes[1, 1], validation_data['basic_stats'])
        
        plt.tight_layout()
        
        # 保存图表
        if save_path is None:
            save_path = f"schedule_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def _get_test_teachers(self) -> List[Dict]:
        """获取测试教师数据"""
        teachers = User.objects.filter(
            username__startswith='smart_teacher_',
            user_type='teacher',
            is_active=True
        )
        
        teacher_list = []
        for teacher in teachers:
            teacher_data = {
                'id': teacher.id,
                'name': f"{teacher.first_name}{teacher.last_name}",
                'department': teacher.department,
                'email': teacher.email,
                'qualified_courses': list(range(1, 20)),  # 假设能教多门课
                'max_weekly_hours': 16,
                'preferred_time_slots': [(1, 2), (2, 3), (3, 4)]  # 偏好时间
            }
            teacher_list.append(teacher_data)
        
        return teacher_list
    
    def _get_test_courses(self) -> List[Dict]:
        """获取测试课程数据"""
        courses = Course.objects.filter(
            code__startswith='SMART_',
            is_active=True,
            is_published=True
        )
        
        course_list = []
        for course in courses:
            course_data = {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'credits': course.credits,
                'max_students': course.max_students,
                'course_type': course.course_type,
                'semester': course.semester,
                'academic_year': course.academic_year,
                'department': course.department,
                'is_active': course.is_active,
                'is_published': course.is_published
            }
            course_list.append(course_data)
        
        return course_list
    
    def _get_test_classrooms(self) -> List[Dict]:
        """获取测试教室数据"""
        # 生成虚拟教室数据
        classrooms = []
        for i in range(1, 21):  # 20个教室
            classroom = {
                'id': i,
                'name': f"教室{i:03d}",
                'building': f"教学楼{chr(65 + i//5)}",  # A, B, C, D楼
                'capacity': 60 + i * 5,
                'room_type': 'lecture' if i <= 15 else 'computer',
                'is_available': True
            }
            classrooms.append(classroom)
        
        return classrooms
    
    def _analyze_time_distribution(self, assignments) -> Dict:
        """分析时间分布"""
        time_slots_usage = defaultdict(int)
        daily_usage = defaultdict(int)
        
        for assignment in assignments:
            time_key = f"{assignment.day_of_week}-{assignment.time_slot}"
            time_slots_usage[time_key] += 1
            daily_usage[assignment.day_of_week] += 1
        
        return {
            'time_slots': dict(time_slots_usage),
            'daily_usage': dict(daily_usage),
            'peak_day': max(daily_usage.items(), key=lambda x: x[1]) if daily_usage else (0, 0),
            'peak_slot': max(time_slots_usage.items(), key=lambda x: x[1]) if time_slots_usage else ("", 0)
        }
    
    def _analyze_teacher_load(self, assignments) -> Dict:
        """分析教师负载"""
        teacher_loads = defaultdict(int)
        teacher_courses = defaultdict(set)
        
        for assignment in assignments:
            teacher_loads[assignment.teacher_id] += 1
            teacher_courses[assignment.teacher_id].add(assignment.course_id)
        
        loads = list(teacher_loads.values())
        
        return {
            'teacher_counts': dict(teacher_loads),
            'course_counts': {tid: len(courses) for tid, courses in teacher_courses.items()},
            'average_load': sum(loads) / len(loads) if loads else 0,
            'max_load': max(loads) if loads else 0,
            'min_load': min(loads) if loads else 0,
            'load_variance': self._calculate_variance(loads)
        }
    
    def _analyze_classroom_usage(self, assignments) -> Dict:
        """分析教室利用率"""
        classroom_usage = defaultdict(int)
        
        for assignment in assignments:
            classroom_usage[assignment.classroom_id] += 1
        
        usage_values = list(classroom_usage.values())
        
        return {
            'usage_counts': dict(classroom_usage),
            'average_usage': sum(usage_values) / len(usage_values) if usage_values else 0,
            'max_usage': max(usage_values) if usage_values else 0,
            'utilization_rate': len([u for u in usage_values if u > 0]) / max(len(usage_values), 1)
        }
    
    def _analyze_course_distribution(self, assignments) -> Dict:
        """分析课程分布"""
        course_times = defaultdict(list)
        
        for assignment in assignments:
            course_times[assignment.course_id].append((assignment.day_of_week, assignment.time_slot))
        
        return {
            'courses_scheduled': len(course_times),
            'average_sessions_per_course': sum(len(times) for times in course_times.values()) / len(course_times) if course_times else 0
        }
    
    def _calculate_quality_score(self, conflicts: int, total: int, time_dist: Dict, teacher_load: Dict) -> float:
        """计算综合质量评分"""
        if total == 0:
            return 0
        
        # 冲突惩罚
        conflict_penalty = (conflicts / total) * 100
        
        # 时间分布均衡性
        daily_usage = list(time_dist['daily_usage'].values())
        time_balance = 100 - (self._calculate_variance(daily_usage) * 10) if daily_usage else 0
        
        # 教师负载均衡性
        load_balance = 100 - (teacher_load['load_variance'] * 5)
        
        # 综合评分
        quality_score = max(0, 100 - conflict_penalty + time_balance * 0.3 + load_balance * 0.2)
        
        return min(100, quality_score)
    
    def _calculate_variance(self, values: List[float]) -> float:
        """计算方差"""
        if not values:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _plot_time_heatmap(self, ax, time_distribution):
        """绘制时间分布热力图"""
        # 创建时间表矩阵
        matrix = [[0 for _ in range(10)] for _ in range(5)]
        
        for time_key, count in time_distribution['time_slots'].items():
            if '-' in time_key:
                day, slot = map(int, time_key.split('-'))
                if 1 <= day <= 5 and 1 <= slot <= 10:
                    matrix[day-1][slot-1] = count
        
        sns.heatmap(matrix, ax=ax, annot=True, fmt='d', cmap='YlOrRd',
                   xticklabels=[f"第{i}节" for i in range(1, 11)],
                   yticklabels=["周一", "周二", "周三", "周四", "周五"])
        ax.set_title('课程时间分布热力图')
        ax.set_xlabel('时间段')
        ax.set_ylabel('星期')
    
    def _plot_teacher_load(self, ax, teacher_load):
        """绘制教师负载分布"""
        loads = list(teacher_load['teacher_counts'].values())
        
        if loads:
            ax.hist(loads, bins=max(10, len(set(loads))), edgecolor='black', alpha=0.7)
            ax.axvline(teacher_load['average_load'], color='red', linestyle='--', 
                      label=f'平均负载: {teacher_load["average_load"]:.1f}')
            ax.set_title('教师授课负载分布')
            ax.set_xlabel('授课数量')
            ax.set_ylabel('教师人数')
            ax.legend()
        else:
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes)
    
    def _plot_classroom_usage(self, ax, classroom_usage):
        """绘制教室利用率"""
        usage_values = list(classroom_usage['usage_counts'].values())
        
        if usage_values:
            ax.bar(range(len(usage_values)), sorted(usage_values, reverse=True))
            ax.set_title('教室使用频次')
            ax.set_xlabel('教室排序')
            ax.set_ylabel('使用次数')
        else:
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes)
    
    def _plot_quality_radar(self, ax, basic_stats):
        """绘制质量指标雷达图"""
        categories = ['无冲突率', '适应度', '质量评分']
        values = [
            (1 - basic_stats['conflict_rate']) * 100,
            basic_stats['fitness_score'],
            basic_stats['quality_score']
        ]
        
        # 雷达图
        angles = [i * 360 / len(categories) for i in range(len(categories))]
        angles += angles[:1]  # 闭合
        values += values[:1]   # 闭合
        
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_title('质量指标评估')
        ax.grid(True)


def main():
    """主函数"""
    print("🎯 课程表验证工具")
    print("=" * 50)
    
    validator = ScheduleValidator()
    
    # 选择算法
    algorithm = input("请选择算法 (greedy/genetic/hybrid) [hybrid]: ").strip() or 'hybrid'
    
    # 运行算法测试
    test_result = validator.run_algorithm_test(algorithm)
    
    if not test_result:
        print("❌ 算法测试失败")
        return
    
    # 验证课程表质量
    validation_data = validator.validate_schedule_quality(test_result['result'])
    
    # 输出基础统计
    if 'basic_stats' in validation_data:
        stats = validation_data['basic_stats']
        print(f"\n📊 课程表质量分析:")
        print(f"   总排课数: {stats['total_assignments']}")
        print(f"   冲突数量: {stats['conflicts']}")
        print(f"   冲突率: {stats['conflict_rate']:.2%}")
        print(f"   适应度: {stats['fitness_score']:.2f}")
        print(f"   质量评分: {stats['quality_score']:.1f}/100")
    
    # 生成可视化报告
    report_path = validator.generate_visual_report(validation_data)
    print(f"\n📋 可视化报告已保存: {report_path}")
    
    print("\n✅ 验证完成！请查看生成的图表了解课程表质量。")


if __name__ == '__main__':
    main()