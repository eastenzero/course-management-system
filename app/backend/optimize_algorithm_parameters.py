#!/usr/bin/env python
"""
算法参数调优脚本
用于优化排课算法的参数以获得最佳效果
"""

import os
import sys
import django
import random
import json
from datetime import datetime
from typing import Dict, List, Tuple

# 添加项目路径（基于脚本位置，提升跨平台兼容性）
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent  # app/backend
sys.path.insert(0, str(BASE_DIR))

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from apps.schedules.genetic_algorithm import GeneticSchedulingAlgorithm
from apps.schedules.hybrid_algorithm import HybridSchedulingAlgorithm
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from apps.users.models import User
from apps.schedules.models import TimeSlot


class ParameterOptimizer:
    """参数优化器"""
    
    def __init__(self, semester: str, academic_year: str):
        self.semester = semester
        self.academic_year = academic_year
        self.best_params = {}
        self.best_score = 0
        
    def optimize_genetic_algorithm(self) -> Dict:
        """
        优化遗传算法参数
        
        Returns:
            最佳参数配置
        """
        print("🧬 开始优化遗传算法参数...")
        
        # 参数搜索空间
        param_space = {
            'population_size': [20, 30, 50],
            'max_generations': [100, 200, 500],
            'crossover_rate': [0.7, 0.8, 0.9],
            'mutation_rate': [0.05, 0.1, 0.15],
            'elite_size': [2, 3, 5]
        }
        
        best_score = 0
        best_params = {}
        
        # 简单网格搜索（实际应用中可以使用更高级的优化方法）
        for pop_size in param_space['population_size']:
            for max_gen in param_space['max_generations']:
                for cross_rate in param_space['crossover_rate']:
                    for mut_rate in param_space['mutation_rate']:
                        for elite_size in param_space['elite_size']:
                            # 确保精英大小不超过种群大小
                            if elite_size >= pop_size:
                                continue
                                
                            params = {
                                'population_size': pop_size,
                                'max_generations': max_gen,
                                'crossover_rate': cross_rate,
                                'mutation_rate': mut_rate,
                                'elite_size': elite_size
                            }
                            
                            print(f"  测试参数: {params}")
                            
                            try:
                                score = self._evaluate_genetic_params(params)
                                print(f"    得分: {score:.2f}")
                                
                                if score > best_score:
                                    best_score = score
                                    best_params = params.copy()
                                    print(f"    🎉 新的最佳参数! 得分: {best_score:.2f}")
                            except Exception as e:
                                print(f"    ❌ 评估失败: {e}")
                                continue
        
        self.best_params['genetic'] = best_params
        self.best_score = best_score
        
        print(f"✅ 遗传算法参数优化完成")
        print(f"   最佳得分: {best_score:.2f}")
        print(f"   最佳参数: {best_params}")
        
        return best_params
    
    def _evaluate_genetic_params(self, params: Dict) -> float:
        """
        评估遗传算法参数
        
        Args:
            params: 参数配置
            
        Returns:
            评估得分
        """
        # 创建遗传算法实例
        algorithm = GeneticSchedulingAlgorithm(
            semester=self.semester,
            academic_year=self.academic_year,
            population_size=params['population_size'],
            max_generations=params['max_generations'],
            crossover_rate=params['crossover_rate'],
            mutation_rate=params['mutation_rate'],
            elite_size=params['elite_size']
        )
        
        # 添加测试约束（使用少量课程以加快评估速度）
        courses = Course.objects.filter(
            semester=self.semester,
            academic_year=self.academic_year,
            is_active=True,
            is_published=True
        )[:20]  # 只使用前20门课程进行参数评估
        
        available_classrooms = list(Classroom.objects.filter(is_active=True))
        available_time_slots = list(TimeSlot.objects.filter(is_active=True))
        
        for course in courses:
            main_teacher = course.teachers.first()
            if not main_teacher:
                continue
                
            # 设置偏好
            preferred_classrooms = available_classrooms
            preferred_time_slots = available_time_slots
            preferred_days = list(range(1, 6))
            
            # 根据课程类型调整偏好
            if course.course_type == 'lab':
                preferred_classrooms = [c for c in available_classrooms if c.room_type == 'lab']
            elif course.course_type == 'lecture':
                preferred_classrooms = [c for c in available_classrooms if c.capacity >= 50]
            
            # 计算每周课时数
            sessions_per_week = min(course.hours // 18, 4)
            if sessions_per_week == 0:
                sessions_per_week = 1
            
            constraint = algorithm.ScheduleConstraint(
                course=course,
                teacher=main_teacher,
                preferred_classrooms=preferred_classrooms,
                preferred_time_slots=preferred_time_slots,
                preferred_days=preferred_days,
                sessions_per_week=sessions_per_week,
                avoid_consecutive=course.course_type == 'lecture',
                priority=3 if course.course_type == 'required' else 2
            )
            
            algorithm.add_constraint(constraint)
        
        # 运行算法
        result = algorithm.solve(timeout_seconds=60)  # 限制评估时间为60秒
        
        # 计算综合得分（成功率权重70% + 时间效率权重30%）
        success_rate = result.get('success_rate', 0)
        execution_time = result.get('execution_time', 1)  # 避免除零
        
        # 时间效率得分（执行时间越短得分越高，但不超过30分）
        time_score = max(0, 30 - min(30, execution_time))
        
        # 综合得分
        total_score = success_rate * 0.7 + time_score
        
        return total_score
    
    def optimize_hybrid_algorithm(self) -> Dict:
        """
        优化混合算法参数
        
        Returns:
            最佳参数配置
        """
        print("🔄 开始优化混合算法参数...")
        
        # 参数搜索空间
        param_space = {
            'population_size': [10, 20, 30],
            'max_generations': [50, 100, 200],
            'crossover_rate': [0.7, 0.8, 0.9],
            'mutation_rate': [0.05, 0.1, 0.15],
            'elite_size': [1, 2, 3],
            'greedy_improvement_rounds': [1, 2, 3]
        }
        
        best_score = 0
        best_params = {}
        
        # 简单网格搜索
        for pop_size in param_space['population_size']:
            for max_gen in param_space['max_generations']:
                for cross_rate in param_space['crossover_rate']:
                    for mut_rate in param_space['mutation_rate']:
                        for elite_size in param_space['elite_size']:
                            for imp_rounds in param_space['greedy_improvement_rounds']:
                                # 确保精英大小不超过种群大小
                                if elite_size >= pop_size:
                                    continue
                                    
                                params = {
                                    'population_size': pop_size,
                                    'max_generations': max_gen,
                                    'crossover_rate': cross_rate,
                                    'mutation_rate': mut_rate,
                                    'elite_size': elite_size,
                                    'greedy_improvement_rounds': imp_rounds
                                }
                                
                                print(f"  测试参数: {params}")
                                
                                try:
                                    score = self._evaluate_hybrid_params(params)
                                    print(f"    得分: {score:.2f}")
                                    
                                    if score > best_score:
                                        best_score = score
                                        best_params = params.copy()
                                        print(f"    🎉 新的最佳参数! 得分: {best_score:.2f}")
                                except Exception as e:
                                    print(f"    ❌ 评估失败: {e}")
                                    continue
        
        self.best_params['hybrid'] = best_params
        if best_score > self.best_score:
            self.best_score = best_score
        
        print(f"✅ 混合算法参数优化完成")
        print(f"   最佳得分: {best_score:.2f}")
        print(f"   最佳参数: {best_params}")
        
        return best_params
    
    def _evaluate_hybrid_params(self, params: Dict) -> float:
        """
        评估混合算法参数
        
        Args:
            params: 参数配置
            
        Returns:
            评估得分
        """
        # 创建混合算法实例
        algorithm = HybridSchedulingAlgorithm(
            semester=self.semester,
            academic_year=self.academic_year,
            population_size=params['population_size'],
            max_generations=params['max_generations'],
            crossover_rate=params['crossover_rate'],
            mutation_rate=params['mutation_rate'],
            elite_size=params['elite_size'],
            greedy_improvement_rounds=params['greedy_improvement_rounds']
        )
        
        # 添加测试约束（使用少量课程以加快评估速度）
        courses = Course.objects.filter(
            semester=self.semester,
            academic_year=self.academic_year,
            is_active=True,
            is_published=True
        )[:15]  # 只使用前15门课程进行参数评估
        
        available_classrooms = list(Classroom.objects.filter(is_active=True))
        available_time_slots = list(TimeSlot.objects.filter(is_active=True))
        
        for course in courses:
            main_teacher = course.teachers.first()
            if not main_teacher:
                continue
                
            # 设置偏好
            preferred_classrooms = available_classrooms
            preferred_time_slots = available_time_slots
            preferred_days = list(range(1, 6))
            
            # 根据课程类型调整偏好
            if course.course_type == 'lab':
                preferred_classrooms = [c for c in available_classrooms if c.room_type == 'lab']
            elif course.course_type == 'lecture':
                preferred_classrooms = [c for c in available_classrooms if c.capacity >= 50]
            
            # 计算每周课时数
            sessions_per_week = min(course.hours // 18, 4)
            if sessions_per_week == 0:
                sessions_per_week = 1
            
            constraint = algorithm.ScheduleConstraint(
                course=course,
                teacher=main_teacher,
                preferred_classrooms=preferred_classrooms,
                preferred_time_slots=preferred_time_slots,
                preferred_days=preferred_days,
                sessions_per_week=sessions_per_week,
                avoid_consecutive=course.course_type == 'lecture',
                priority=3 if course.course_type == 'required' else 2
            )
            
            algorithm.add_constraint(constraint)
        
        # 运行算法
        result = algorithm.solve(timeout_seconds=60)  # 限制评估时间为60秒
        
        # 计算综合得分
        success_rate = result.get('success_rate', 0)
        execution_time = result.get('execution_time', 1)  # 避免除零
        
        # 时间效率得分
        time_score = max(0, 30 - min(30, execution_time))
        
        # 综合得分
        total_score = success_rate * 0.7 + time_score
        
        return total_score
    
    def generate_recommendation_report(self) -> str:
        """
        生成参数推荐报告
        
        Returns:
            报告文本
        """
        report = []
        report.append("=" * 60)
        report.append("智能排课算法参数优化推荐报告")
        report.append("=" * 60)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"学期: {self.semester}")
        report.append(f"学年: {self.academic_year}")
        report.append("")
        
        # 遗传算法推荐
        if 'genetic' in self.best_params:
            report.append("🧬 遗传算法推荐参数:")
            report.append("-" * 30)
            genetic_params = self.best_params['genetic']
            for key, value in genetic_params.items():
                report.append(f"  {key}: {value}")
            report.append("")
        
        # 混合算法推荐
        if 'hybrid' in self.best_params:
            report.append("🔄 混合算法推荐参数:")
            report.append("-" * 30)
            hybrid_params = self.best_params['hybrid']
            for key, value in hybrid_params.items():
                report.append(f"  {key}: {value}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def run_parameter_optimization(semester: str, academic_year: str) -> Dict:
    """
    运行参数优化
    
    Args:
        semester: 学期
        academic_year: 学年
        
    Returns:
        优化结果
    """
    optimizer = ParameterOptimizer(semester, academic_year)
    
    # 优化遗传算法参数
    genetic_params = optimizer.optimize_genetic_algorithm()
    
    # 优化混合算法参数
    hybrid_params = optimizer.optimize_hybrid_algorithm()
    
    # 生成报告
    report = optimizer.generate_recommendation_report()
    print(report)
    
    return {
        'genetic_algorithm': genetic_params,
        'hybrid_algorithm': hybrid_params,
        'report': report
    }


def main():
    """主函数"""
    print("🎯 算法参数优化工具")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 优化参数
    try:
        results = run_parameter_optimization("2024春", "2023-2024")
        
        # 保存结果到文件
        with open('algorithm_parameter_recommendations.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print()
        print("✅ 参数优化完成，结果已保存到 algorithm_parameter_recommendations.json")
        
    except Exception as e:
        print(f"❌ 参数优化过程中发生错误: {e}")
    
    print()
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 参数优化完成!")


if __name__ == "__main__":
    main()