"""
遗传算法排课模块
实现基于遗传算法的智能排课算法
"""

import random
import copy
import numpy as np
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

from .algorithms import SchedulingAlgorithm, ScheduleConstraint, ScheduleSlot
from .models import Schedule, TimeSlot
from apps.courses.models import Course
from apps.classrooms.models import Classroom
from apps.users.models import User


@dataclass
class Individual:
    """个体类 - 代表一个完整的排课方案"""
    chromosome: Dict[ScheduleConstraint, List[ScheduleSlot]]  # 染色体：约束到时间槽的映射
    fitness: float = 0.0  # 适应度
    
    def __hash__(self):
        # 基于染色体内容计算哈希值
        hash_value = 0
        for constraint, slots in self.chromosome.items():
            hash_value ^= hash((constraint, tuple(slots)))
        return hash_value


class GeneticSchedulingAlgorithm(SchedulingAlgorithm):
    """遗传算法排课"""
    
    def __init__(self, semester: str, academic_year: str,
                 population_size: int = 50,
                 max_generations: int = 1000,
                 crossover_rate: float = 0.8,
                 mutation_rate: float = 0.1,
                 elite_size: int = 5):
        super().__init__(semester, academic_year)
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        
        # 遗传算法特有的属性
        self.population: List[Individual] = []
        self.best_individual: Individual = None
        self.fitness_history: List[float] = []
        
    def initialize_population(self):
        """初始化种群"""
        print(f"🧬 初始化种群，大小: {self.population_size}")
        self.population = []
        
        # 使用贪心算法生成初始个体
        greedy_algorithm = SchedulingAlgorithm(self.semester, self.academic_year)
        
        # 复制约束
        for constraint in self.constraints:
            greedy_algorithm.add_constraint(constraint)
        
        # 生成精英个体（使用贪心算法）
        for i in range(min(self.elite_size, self.population_size)):
            print(f"  生成精英个体 {i+1}/{self.elite_size}")
            # 运行贪心算法
            greedy_result = greedy_algorithm.solve()
            
            # 创建个体
            chromosome = {}
            if 'assigned_slots' in greedy_result:
                chromosome = copy.deepcopy(greedy_result['assigned_slots'])
            
            individual = Individual(chromosome=chromosome)
            self.calculate_fitness(individual)
            self.population.append(individual)
            
            # 重置贪心算法的状态
            greedy_algorithm.assigned_slots.clear()
            greedy_algorithm.teacher_schedule.clear()
            greedy_algorithm.classroom_schedule.clear()
            greedy_algorithm.available_slots.clear()
        
        # 生成随机个体填充剩余位置
        for i in range(len(self.population), self.population_size):
            print(f"  生成随机个体 {i+1}/{self.population_size}")
            chromosome = self._generate_random_chromosome()
            individual = Individual(chromosome=chromosome)
            self.calculate_fitness(individual)
            self.population.append(individual)
        
        print(f"✅ 种群初始化完成，共 {len(self.population)} 个个体")
    
    def _generate_random_chromosome(self) -> Dict[ScheduleConstraint, List[ScheduleSlot]]:
        """生成随机染色体"""
        chromosome = {}
        
        # 为每个约束随机分配时间槽
        for constraint in self.constraints:
            # 随机选择时间槽
            slots = []
            for _ in range(constraint.sessions_per_week):
                if self.available_slots:
                    slot = random.choice(list(self.available_slots))
                    slots.append(slot)
            
            chromosome[constraint] = slots
        
        return chromosome
    
    def calculate_fitness(self, individual: Individual):
        """计算个体适应度"""
        # 适应度由多个因素组成：
        # 1. 硬约束满足程度（必须完全满足）
        # 2. 软约束满足程度（偏好、平衡等）
        # 3. 优化目标（教室利用率、时间分布等）
        
        hard_constraint_score = self._calculate_hard_constraint_score(individual)
        soft_constraint_score = self._calculate_soft_constraint_score(individual)
        optimization_score = self._calculate_optimization_score(individual)
        
        # 如果硬约束不满足，适应度为负值
        if hard_constraint_score < 1.0:
            individual.fitness = -1000 * (1.0 - hard_constraint_score)
        else:
            # 综合评分
            individual.fitness = (
                hard_constraint_score * 1000 +
                soft_constraint_score * 100 +
                optimization_score * 50
            )
    
    def _calculate_hard_constraint_score(self, individual: Individual) -> float:
        """计算硬约束满足分数"""
        conflicts = 0
        total_assignments = 0
        
        # 检查每个约束的分配
        for constraint, slots in individual.chromosome.items():
            total_assignments += len(slots)
            
            # 检查教师时间冲突
            teacher_slots = defaultdict(int)
            for slot in slots:
                time_key = (slot.day_of_week, slot.time_slot.id)
                teacher_slots[time_key] += 1
                # 检查教室时间冲突
                classroom_time_key = (slot.classroom.id, slot.day_of_week, slot.time_slot.id)
            
            # 检查教师是否在同时间有多个课程
            for count in teacher_slots.values():
                if count > 1:
                    conflicts += count - 1
            
            # 检查教室是否在同时间有多个课程
            classroom_slots = defaultdict(int)
            for slot in slots:
                classroom_time_key = (slot.classroom.id, slot.day_of_week, slot.time_slot.id)
                classroom_slots[classroom_time_key] += 1
            
            for count in classroom_slots.values():
                if count > 1:
                    conflicts += count - 1
        
        # 计算满足度
        if total_assignments == 0:
            return 0.0
        
        return max(0.0, 1.0 - (conflicts / total_assignments))
    
    def _calculate_soft_constraint_score(self, individual: Individual) -> float:
        """计算软约束满足分数"""
        total_score = 0.0
        total_constraints = len(individual.chromosome)
        
        if total_constraints == 0:
            return 0.0
        
        for constraint, slots in individual.chromosome.items():
            constraint_score = 0.0
            
            # 偏好教室满足度
            preferred_classroom_count = sum(
                1 for slot in slots if slot.classroom in constraint.preferred_classrooms
            )
            if constraint.preferred_classrooms:
                constraint_score += (preferred_classroom_count / len(slots)) * 0.3
            
            # 偏好时间段满足度
            preferred_time_count = sum(
                1 for slot in slots if slot.time_slot in constraint.preferred_time_slots
            )
            if constraint.preferred_time_slots:
                constraint_score += (preferred_time_count / len(slots)) * 0.3
            
            # 偏好星期满足度
            preferred_day_count = sum(
                1 for slot in slots if slot.day_of_week in constraint.preferred_days
            )
            if constraint.preferred_days:
                constraint_score += (preferred_day_count / len(slots)) * 0.2
            
            # 避免连续排课
            if constraint.avoid_consecutive:
                consecutive_count = self._count_consecutive_classes(slots)
                constraint_score += ((len(slots) - consecutive_count) / len(slots)) * 0.2
            else:
                constraint_score += 0.2  # 如果不需要避免连续，则满分
            
            total_score += constraint_score
        
        return total_score / total_constraints
    
    def _count_consecutive_classes(self, slots: List[ScheduleSlot]) -> int:
        """计算连续排课数量"""
        consecutive_count = 0
        sorted_slots = sorted(slots, key=lambda s: (s.day_of_week, s.time_slot.order))
        
        for i in range(len(sorted_slots) - 1):
            current = sorted_slots[i]
            next_slot = sorted_slots[i + 1]
            
            # 如果在同一天且时间连续
            if (current.day_of_week == next_slot.day_of_week and
                next_slot.time_slot.order == current.time_slot.order + 1):
                consecutive_count += 1
        
        return consecutive_count
    
    def _calculate_optimization_score(self, individual: Individual) -> float:
        """计算优化目标分数"""
        # 分析教室利用率和时间分布
        classroom_usage = defaultdict(int)
        time_distribution = defaultdict(int)
        
        for slots in individual.chromosome.values():
            for slot in slots:
                classroom_usage[slot.classroom.id] += 1
                time_key = (slot.day_of_week, slot.time_slot.id)
                time_distribution[time_key] += 1
        
        # 教室利用率平衡度
        if classroom_usage:
            usage_values = list(classroom_usage.values())
            avg_usage = sum(usage_values) / len(usage_values)
            usage_variance = np.var(usage_values) if len(usage_values) > 1 else 0
            classroom_balance_score = max(0.0, 1.0 - (usage_variance / (avg_usage + 1)))
        else:
            classroom_balance_score = 0.0
        
        # 时间分布平衡度
        if time_distribution:
            distribution_values = list(time_distribution.values())
            avg_distribution = sum(distribution_values) / len(distribution_values)
            distribution_variance = np.var(distribution_values) if len(distribution_values) > 1 else 0
            time_balance_score = max(0.0, 1.0 - (distribution_variance / (avg_distribution + 1)))
        else:
            time_balance_score = 0.0
        
        return (classroom_balance_score + time_balance_score) / 2
    
    def selection(self) -> List[Individual]:
        """选择操作 - 锦标赛选择"""
        selected = []
        tournament_size = 3
        
        # 保留精英个体
        sorted_population = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        elite_individuals = sorted_population[:self.elite_size]
        
        # 锦标赛选择其余个体
        for _ in range(self.population_size - self.elite_size):
            # 随机选择锦标赛参与者
            tournament = random.sample(self.population, min(tournament_size, len(self.population)))
            # 选择适应度最高的个体
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(copy.deepcopy(winner))
        
        # 将精英个体加入选择结果
        selected.extend(copy.deepcopy(elite_individuals))
        
        return selected
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """交叉操作 - 均匀交叉"""
        if random.random() > self.crossover_rate:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        # 创建子代染色体
        child1_chromosome = {}
        child2_chromosome = {}
        
        # 对每个约束进行交叉
        all_constraints = set(parent1.chromosome.keys()) | set(parent2.chromosome.keys())
        
        for constraint in all_constraints:
            if constraint in parent1.chromosome and constraint in parent2.chromosome:
                # 均匀交叉：随机选择来自哪个父代
                if random.random() < 0.5:
                    child1_chromosome[constraint] = copy.deepcopy(parent1.chromosome[constraint])
                    child2_chromosome[constraint] = copy.deepcopy(parent2.chromosome[constraint])
                else:
                    child1_chromosome[constraint] = copy.deepcopy(parent2.chromosome[constraint])
                    child2_chromosome[constraint] = copy.deepcopy(parent1.chromosome[constraint])
            elif constraint in parent1.chromosome:
                # 只在父代1中存在
                child1_chromosome[constraint] = copy.deepcopy(parent1.chromosome[constraint])
                # 父代2中不存在，随机生成
                child2_chromosome[constraint] = self._generate_random_slots_for_constraint(constraint)
            else:
                # 只在父代2中存在
                child2_chromosome[constraint] = copy.deepcopy(parent2.chromosome[constraint])
                # 父代1中不存在，随机生成
                child1_chromosome[constraint] = self._generate_random_slots_for_constraint(constraint)
        
        child1 = Individual(chromosome=child1_chromosome)
        child2 = Individual(chromosome=child2_chromosome)
        
        return child1, child2
    
    def _generate_random_slots_for_constraint(self, constraint: ScheduleConstraint) -> List[ScheduleSlot]:
        """为约束生成随机时间槽"""
        slots = []
        for _ in range(constraint.sessions_per_week):
            if self.available_slots:
                slot = random.choice(list(self.available_slots))
                slots.append(slot)
        return slots
    
    def mutate(self, individual: Individual) -> Individual:
        """变异操作"""
        if random.random() > self.mutation_rate:
            return individual
        
        # 随机选择一个约束进行变异
        if not individual.chromosome:
            return individual
        
        constraint = random.choice(list(individual.chromosome.keys()))
        # 重新为该约束生成时间槽
        individual.chromosome[constraint] = self._generate_random_slots_for_constraint(constraint)
        
        return individual
    
    def solve(self) -> Dict:
        """执行遗传算法排课"""
        print("🧬 开始遗传算法排课...")
        print(f"  📊 约束数量: {len(self.constraints)}")
        print(f"  👥 可用时间槽: {len(self.available_slots)}")
        
        # 初始化种群
        self.initialize_population()
        
        # 初始化最优个体
        self.best_individual = max(self.population, key=lambda x: x.fitness)
        
        # 进化过程
        for generation in range(self.max_generations):
            # 计算所有个体的适应度
            for individual in self.population:
                self.calculate_fitness(individual)
            
            # 更新最优个体
            current_best = max(self.population, key=lambda x: x.fitness)
            if current_best.fitness > self.best_individual.fitness:
                self.best_individual = copy.deepcopy(current_best)
            
            # 记录适应度历史
            self.fitness_history.append(self.best_individual.fitness)
            
            # 检查收敛条件
            if generation > 100 and len(set(self.fitness_history[-50:])) == 1:
                print(f"  ⏹️  算法收敛，提前终止于第 {generation} 代")
                break
            
            # 打印进度
            if generation % 100 == 0 or generation == self.max_generations - 1:
                print(f"  🔁 第 {generation} 代: 最佳适应度 = {self.best_individual.fitness:.2f}")
            
            # 选择
            selected = self.selection()
            
            # 交叉和变异生成新种群
            new_population = []
            
            # 保持精英个体
            sorted_selected = sorted(selected, key=lambda x: x.fitness, reverse=True)
            new_population.extend(sorted_selected[:self.elite_size])
            
            # 交叉和变异生成其余个体
            for i in range(self.elite_size, self.population_size, 2):
                parent1 = selected[i]
                parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]
                
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.extend([child1, child2])
            
            # 确保种群大小正确
            self.population = new_population[:self.population_size]
        
        # 准备返回结果
        successful_assignments = 0
        failed_assignments = []
        total_constraints = len(self.best_individual.chromosome)
        
        # 分析每个约束的分配结果
        for constraint, slots in self.best_individual.chromosome.items():
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
        
        # 更新分配结果
        self.assigned_slots = self.best_individual.chromosome
        
        result = {
            'successful_assignments': successful_assignments,
            'failed_assignments': failed_assignments,
            'total_constraints': total_constraints,
            'success_rate': success_rate,
            'assigned_slots': self.assigned_slots,
            'best_fitness': self.best_individual.fitness,
            'generations': len(self.fitness_history),
            'optimization_suggestions': self.get_optimization_suggestions()
        }
        
        print(f"✅ 遗传算法完成:")
        print(f"  📈 最佳适应度: {self.best_individual.fitness:.2f}")
        print(f"  🎯 成功率: {success_rate:.1f}%")
        print(f"  🔄 进化代数: {len(self.fitness_history)}")
        
        return result


def create_genetic_schedule(semester: str, academic_year: str, course_ids: List[int] = None) -> Dict:
    """
    遗传算法自动排课主函数
    
    Args:
        semester: 学期
        academic_year: 学年
        course_ids: 要排课的课程ID列表，如果为None则排所有课程
    
    Returns:
        排课结果字典
    """
    print(f"🧬 开始遗传算法排课: {semester} {academic_year}")
    
    # 创建遗传算法实例
    algorithm = GeneticSchedulingAlgorithm(
        semester=semester,
        academic_year=academic_year,
        population_size=30,      # 种群大小
        max_generations=500,     # 最大进化代数
        crossover_rate=0.8,      # 交叉率
        mutation_rate=0.1,       # 变异率
        elite_size=3             # 精英个体数量
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
        'algorithm_instance': algorithm  # 用于后续创建Schedule对象
    })
    
    return result