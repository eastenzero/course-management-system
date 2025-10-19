"""
混合算法排课模块
实现结合贪心算法和遗传算法优势的智能排课算法
"""

import random
import copy
import time
import numpy as np
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

from .algorithms import SchedulingAlgorithm, ScheduleConstraint, ScheduleSlot, create_auto_schedule
from .genetic_algorithm import GeneticSchedulingAlgorithm, Individual
from .models import Schedule, TimeSlot
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from apps.users.models import User


class HybridSchedulingAlgorithm(SchedulingAlgorithm):
    """混合算法排课 - 结合贪心算法和遗传算法"""
    
    def __init__(self, semester: str, academic_year: str,
                 population_size: int = 30,
                 max_generations: int = 200,
                 crossover_rate: float = 0.8,
                 mutation_rate: float = 0.1,
                 elite_size: int = 3,
                 greedy_improvement_rounds: int = 3):
        super().__init__(semester, academic_year)
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.greedy_improvement_rounds = greedy_improvement_rounds
        
        # 混合算法特有的属性
        self.population: List[Individual] = []
        self.best_individual: Individual = None
        self.fitness_history: List[float] = []
        
    def solve(self, timeout_seconds: int = 300) -> Dict:
        """执行混合算法排课"""
        print("🔄 开始混合算法排课...")
        start_time = time.time()
        
        # 阶段1: 使用贪心算法生成初始解
        print("  🧠 阶段1: 贪心算法生成初始解")
        greedy_result = self._solve_with_greedy()
        
        # 检查超时
        if time.time() - start_time > timeout_seconds:
            return self._create_result_from_greedy(greedy_result, time.time() - start_time, "超时")
        
        # 阶段2: 使用遗传算法优化
        print("  🧬 阶段2: 遗传算法优化")
        genetic_result = self._solve_with_genetic(greedy_result, start_time, timeout_seconds)
        
        # 检查超时
        if time.time() - start_time > timeout_seconds:
            return self._create_result_from_greedy(greedy_result, time.time() - start_time, "超时")
        
        # 阶段3: 局部优化
        print("  🔧 阶段3: 局部优化")
        final_result = self._local_optimization(genetic_result, start_time, timeout_seconds)
        
        execution_time = time.time() - start_time
        return self._create_final_result(final_result, execution_time)
    
    def _solve_with_greedy(self) -> Dict:
        """使用贪心算法生成初始解"""
        # 创建贪心算法实例
        greedy_algorithm = SchedulingAlgorithm(self.semester, self.academic_year)
        
        # 复制约束
        for constraint in self.constraints:
            greedy_algorithm.add_constraint(constraint)
        
        # 执行贪心算法
        result = greedy_algorithm.solve()
        
        return result
    
    def _solve_with_genetic(self, greedy_result: Dict, start_time: float, timeout_seconds: int) -> Dict:
        """使用遗传算法优化贪心算法的结果"""
        # 创建遗传算法实例
        genetic_algorithm = GeneticSchedulingAlgorithm(
            semester=self.semester,
            academic_year=self.academic_year,
            population_size=self.population_size,
            max_generations=self.max_generations,
            crossover_rate=self.crossover_rate,
            mutation_rate=self.mutation_rate,
            elite_size=self.elite_size
        )
        
        # 复制约束
        for constraint in self.constraints:
            genetic_algorithm.add_constraint(constraint)
        
        # 使用贪心算法的结果作为初始种群的一部分
        if 'assigned_slots' in greedy_result and greedy_result['assigned_slots']:
            # 将贪心算法的结果转换为遗传算法的个体
            chromosome = copy.deepcopy(greedy_result['assigned_slots'])
            elite_individual = Individual(chromosome=chromosome)
            
            # 设置初始种群，将贪心算法的结果作为精英个体
            genetic_algorithm.population = [elite_individual]
            
            # 填充剩余种群
            genetic_algorithm.initialize_population()
        else:
            # 如果贪心算法没有结果，正常初始化种群
            genetic_algorithm.initialize_population()
        
        # 执行遗传算法优化
        remaining_time = timeout_seconds - (time.time() - start_time)
        genetic_result = genetic_algorithm.solve()
        
        return genetic_result
    
    def _local_optimization(self, genetic_result: Dict, start_time: float, timeout_seconds: int) -> Dict:
        """局部优化 - 对遗传算法结果进行改进"""
        # 如果遗传算法产生了结果，使用其最佳个体
        if hasattr(genetic_result.get('algorithm_instance'), 'best_individual'):
            best_individual = genetic_result['algorithm_instance'].best_individual
            self.assigned_slots = copy.deepcopy(best_individual.chromosome)
        elif 'assigned_slots' in genetic_result:
            self.assigned_slots = copy.deepcopy(genetic_result['assigned_slots'])
        else:
            # 回退到贪心算法结果
            return genetic_result
        
        # 多轮局部优化
        for round_num in range(self.greedy_improvement_rounds):
            # 检查超时
            if time.time() - start_time > timeout_seconds:
                break
            
            print(f"    🔧 局部优化轮次 {round_num + 1}/{self.greedy_improvement_rounds}")
            
            # 尝试重新安排失败的约束
            failed_constraints = self._get_failed_constraints()
            if not failed_constraints:
                break
            
            # 对每个失败的约束尝试重新安排
            for constraint in failed_constraints:
                if time.time() - start_time > timeout_seconds:
                    break
                
                # 尝试为约束找到更好的时间槽
                self._improve_constraint_assignment(constraint)
        
        # 更新结果
        genetic_result['assigned_slots'] = self.assigned_slots
        return genetic_result
    
    def _get_failed_constraints(self) -> List[ScheduleConstraint]:
        """获取未完全满足的约束"""
        failed_constraints = []
        
        for constraint, slots in self.assigned_slots.items():
            if len(slots) < constraint.sessions_per_week:
                failed_constraints.append(constraint)
        
        return failed_constraints
    
    def _improve_constraint_assignment(self, constraint: ScheduleConstraint):
        """改进约束的分配"""
        # 获取当前分配的时间槽
        current_slots = self.assigned_slots.get(constraint, [])
        
        # 尝试找到更好的时间槽
        best_slots = self.find_best_slots(constraint)
        
        # 如果找到更好的分配，更新
        if len(best_slots) > len(current_slots):
            self.assigned_slots[constraint] = best_slots
            
            # 更新冲突跟踪
            self._update_conflict_tracking(constraint, best_slots)
    
    def _create_result_from_greedy(self, greedy_result: Dict, execution_time: float, termination_reason: str) -> Dict:
        """从贪心算法结果创建返回结果"""
        successful_assignments = 0
        failed_assignments = []
        total_constraints = len(self.constraints)
        
        # 分析每个约束的分配结果
        for constraint in self.constraints:
            slots = greedy_result.get('assigned_slots', {}).get(constraint, [])
            if len(slots) >= constraint.sessions_per_week:
                successful_assignments += 1
            else:
                failed_assignments.append({
                    'constraint': constraint,
                    'assigned_slots': len(slots),
                    'required_slots': constraint.sessions_per_week,
                    'reason': f'分配了 {len(slots)} 个时间槽，需要 {constraint.sessions_per_week} 个'
                })
        
        success_rate = (successful_assignments / total_constraints * 100) if total_constraints > 0 else 0
        
        return {
            'successful_assignments': successful_assignments,
            'failed_assignments': failed_assignments,
            'total_constraints': total_constraints,
            'success_rate': success_rate,
            'assigned_slots': greedy_result.get('assigned_slots', {}),
            'termination_reason': termination_reason,
            'execution_time': execution_time,
            'optimization_suggestions': self.get_optimization_suggestions()
        }
    
    def _create_final_result(self, final_result: Dict, execution_time: float) -> Dict:
        """创建最终返回结果"""
        successful_assignments = 0
        failed_assignments = []
        total_constraints = len(self.constraints)
        
        # 分析每个约束的分配结果
        assigned_slots = final_result.get('assigned_slots', {})
        for constraint in self.constraints:
            slots = assigned_slots.get(constraint, [])
            if len(slots) >= constraint.sessions_per_week:
                successful_assignments += 1
            else:
                failed_assignments.append({
                    'constraint': constraint,
                    'assigned_slots': len(slots),
                    'required_slots': constraint.sessions_per_week,
                    'reason': f'分配了 {len(slots)} 个时间槽，需要 {constraint.sessions_per_week} 个'
                })
        
        success_rate = (successful_assignments / total_constraints * 100) if total_constraints > 0 else 0
        
        return {
            'successful_assignments': successful_assignments,
            'failed_assignments': failed_assignments,
            'total_constraints': total_constraints,
            'success_rate': success_rate,
            'assigned_slots': assigned_slots,
            'execution_time': execution_time,
            'optimization_suggestions': self.get_optimization_suggestions()
        }


def create_hybrid_schedule(semester: str, academic_year: str, course_ids: List[int] = None) -> Dict:
    """
    混合算法自动排课主函数
    
    Args:
        semester: 学期
        academic_year: 学年
        course_ids: 要排课的课程ID列表，如果为None则排所有课程
    
    Returns:
        排课结果字典
    """
    print(f"🔄 开始混合算法排课: {semester} {academic_year}")
    
    # 创建混合算法实例
    algorithm = HybridSchedulingAlgorithm(
        semester=semester,
        academic_year=academic_year,
        population_size=20,       # 种群大小
        max_generations=100,      # 最大进化代数
        crossover_rate=0.8,       # 交叉率
        mutation_rate=0.1,        # 变异率
        elite_size=2,             # 精英个体数量
        greedy_improvement_rounds=2  # 贪心改进轮次
    )
    
    # 获取需要排课的课程
    courses_query = Course.objects.filter(
        semester=semester,
        academic_year=academic_year,
        is_active=True,
        is_published=True
    ).select_related().prefetch_related('teachers')
    
    if course_ids:
        courses_query = courses_query.filter(id__in=course_ids)
    
    # 获取可用资源
    available_classrooms = list(Classroom.objects.filter(is_active=True))
    available_time_slots = list(TimeSlot.objects.filter(is_active=True))
    
    # 为每个课程创建约束
    for course in courses_query:
        # 获取课程的主要教师
        main_teacher = course.teachers.first()
        if not main_teacher:
            continue
            
        # 根据课程类型设置偏好
        preferred_classrooms = available_classrooms
        preferred_time_slots = available_time_slots
        preferred_days = list(range(1, 6))  # 周一到周五
        
        # 根据课程类型调整偏好
        if course.course_type == 'lab':
            # 实验课偏好实验室
            preferred_classrooms = [c for c in available_classrooms if c.room_type == 'lab']
        elif course.course_type == 'lecture':
            # 理论课偏好大教室
            preferred_classrooms = [c for c in available_classrooms if c.capacity >= 50]
        
        # 计算每周课时数（简化计算）
        sessions_per_week = min(course.hours // 18, 4)  # 假设18周，最多4次/周
        if sessions_per_week == 0:
            sessions_per_week = 1
        
        constraint = ScheduleConstraint(
            course=course,
            teacher=main_teacher,
            preferred_classrooms=preferred_classrooms,
            preferred_time_slots=preferred_time_slots,
            preferred_days=preferred_days,
            sessions_per_week=sessions_per_week,
            avoid_consecutive=course.course_type == 'lecture',  # 理论课避免连续
            avoid_noon=False,  # 默认不禁用中午时间
            max_daily_sessions=0,  # 默认无每日限制
            priority=3 if course.course_type == 'required' else 2  # 必修课优先级高
        )
        
        algorithm.add_constraint(constraint)
    
    # 执行排课算法
    result = algorithm.solve()
    
    # 生成优化建议
    suggestions = algorithm.get_optimization_suggestions()
    
    # 准备返回结果
    result.update({
        'suggestions': suggestions,
        'algorithm_instance': algorithm,  # 用于后续创建Schedule对象
        'algorithm_type': 'hybrid'
    })
    
    return result