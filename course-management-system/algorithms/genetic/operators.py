# file: algorithms/genetic/operators.py
# 功能: 遗传算法操作符 - 选择、交叉、变异

import random
import numpy as np
from typing import List, Tuple, Dict, Any
from .individual import Individual
from ..models import Assignment


class SelectionOperator:
    """选择操作符"""
    
    @staticmethod
    def tournament_selection(population: List[Individual], tournament_size: int = 3) -> Individual:
        """锦标赛选择"""
        if tournament_size > len(population):
            tournament_size = len(population)
        
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
    
    @staticmethod
    def roulette_wheel_selection(population: List[Individual]) -> Individual:
        """轮盘赌选择"""
        # 处理负适应度值
        min_fitness = min(ind.fitness for ind in population)
        if min_fitness < 0:
            adjusted_fitness = [ind.fitness - min_fitness + 1 for ind in population]
        else:
            adjusted_fitness = [ind.fitness for ind in population]
        
        total_fitness = sum(adjusted_fitness)
        if total_fitness == 0:
            return random.choice(population)
        
        # 计算选择概率
        probabilities = [f / total_fitness for f in adjusted_fitness]
        
        # 轮盘赌选择
        r = random.random()
        cumulative_prob = 0
        for i, prob in enumerate(probabilities):
            cumulative_prob += prob
            if r <= cumulative_prob:
                return population[i]
        
        return population[-1]  # 备选
    
    @staticmethod
    def rank_selection(population: List[Individual]) -> Individual:
        """排名选择"""
        # 按适应度排序
        sorted_population = sorted(population, key=lambda x: x.fitness)
        
        # 计算排名权重
        n = len(population)
        ranks = list(range(1, n + 1))
        total_rank = sum(ranks)
        
        # 轮盘赌选择
        r = random.random() * total_rank
        cumulative_rank = 0
        for i, rank in enumerate(ranks):
            cumulative_rank += rank
            if r <= cumulative_rank:
                return sorted_population[i]
        
        return sorted_population[-1]
    
    @staticmethod
    def elite_selection(population: List[Individual], elite_size: int) -> List[Individual]:
        """精英选择"""
        sorted_population = sorted(population, key=lambda x: x.fitness, reverse=True)
        return sorted_population[:elite_size]


class CrossoverOperator:
    """交叉操作符"""
    
    @staticmethod
    def single_point_crossover(parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """单点交叉"""
        if len(parent1.assignments) != len(parent2.assignments):
            raise ValueError("Parents must have the same number of assignments")
        
        if len(parent1.assignments) <= 1:
            return parent1.copy(), parent2.copy()
        
        # 选择交叉点
        crossover_point = random.randint(1, len(parent1.assignments) - 1)
        
        # 创建子代
        child1_assignments = (parent1.assignments[:crossover_point] + 
                            parent2.assignments[crossover_point:])
        child2_assignments = (parent2.assignments[:crossover_point] + 
                            parent1.assignments[crossover_point:])
        
        child1 = Individual(assignments=child1_assignments)
        child2 = Individual(assignments=child2_assignments)
        
        child1.generation = max(parent1.generation, parent2.generation) + 1
        child2.generation = max(parent1.generation, parent2.generation) + 1
        
        return child1, child2
    
    @staticmethod
    def two_point_crossover(parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """两点交叉"""
        if len(parent1.assignments) != len(parent2.assignments):
            raise ValueError("Parents must have the same number of assignments")
        
        if len(parent1.assignments) <= 2:
            return CrossoverOperator.single_point_crossover(parent1, parent2)
        
        # 选择两个交叉点
        point1 = random.randint(1, len(parent1.assignments) - 2)
        point2 = random.randint(point1 + 1, len(parent1.assignments) - 1)
        
        # 创建子代
        child1_assignments = (parent1.assignments[:point1] + 
                            parent2.assignments[point1:point2] + 
                            parent1.assignments[point2:])
        child2_assignments = (parent2.assignments[:point1] + 
                            parent1.assignments[point1:point2] + 
                            parent2.assignments[point2:])
        
        child1 = Individual(assignments=child1_assignments)
        child2 = Individual(assignments=child2_assignments)
        
        child1.generation = max(parent1.generation, parent2.generation) + 1
        child2.generation = max(parent1.generation, parent2.generation) + 1
        
        return child1, child2
    
    @staticmethod
    def uniform_crossover(parent1: Individual, parent2: Individual, 
                         crossover_probability: float = 0.5) -> Tuple[Individual, Individual]:
        """均匀交叉"""
        if len(parent1.assignments) != len(parent2.assignments):
            raise ValueError("Parents must have the same number of assignments")
        
        child1_assignments = []
        child2_assignments = []
        
        for i in range(len(parent1.assignments)):
            if random.random() < crossover_probability:
                child1_assignments.append(parent1.assignments[i].copy())
                child2_assignments.append(parent2.assignments[i].copy())
            else:
                child1_assignments.append(parent2.assignments[i].copy())
                child2_assignments.append(parent1.assignments[i].copy())
        
        child1 = Individual(assignments=child1_assignments)
        child2 = Individual(assignments=child2_assignments)
        
        child1.generation = max(parent1.generation, parent2.generation) + 1
        child2.generation = max(parent1.generation, parent2.generation) + 1
        
        return child1, child2
    
    @staticmethod
    def course_based_crossover(parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """基于课程的交叉 - 保持课程分配的完整性"""
        # 获取所有课程ID
        all_courses = set(a.course_id for a in parent1.assignments)
        
        # 随机选择一半课程从parent1继承，另一半从parent2继承
        courses_from_parent1 = set(random.sample(list(all_courses), len(all_courses) // 2))
        
        child1_assignments = []
        child2_assignments = []
        
        # 从parent1和parent2中选择对应课程的分配
        for course_id in all_courses:
            if course_id in courses_from_parent1:
                # child1从parent1继承，child2从parent2继承
                assignment1 = next(a for a in parent1.assignments if a.course_id == course_id)
                assignment2 = next(a for a in parent2.assignments if a.course_id == course_id)
            else:
                # child1从parent2继承，child2从parent1继承
                assignment1 = next(a for a in parent2.assignments if a.course_id == course_id)
                assignment2 = next(a for a in parent1.assignments if a.course_id == course_id)
            
            child1_assignments.append(assignment1.copy())
            child2_assignments.append(assignment2.copy())
        
        child1 = Individual(assignments=child1_assignments)
        child2 = Individual(assignments=child2_assignments)
        
        child1.generation = max(parent1.generation, parent2.generation) + 1
        child2.generation = max(parent1.generation, parent2.generation) + 1
        
        return child1, child2


class MutationOperator:
    """变异操作符"""
    
    @staticmethod
    def random_mutation(individual: Individual, teachers: List[Dict], 
                       classrooms: List[Dict], mutation_probability: float = 0.1) -> Individual:
        """随机变异"""
        mutated = individual.copy()
        
        for i, assignment in enumerate(mutated.assignments):
            if random.random() < mutation_probability:
                # 随机选择变异类型
                mutation_type = random.choice(['teacher', 'classroom', 'time'])
                
                if mutation_type == 'teacher':
                    # 变异教师
                    qualified_teachers = [t for t in teachers 
                                        if assignment.course_id in t.get('qualified_courses', [])]
                    if qualified_teachers:
                        new_teacher = random.choice(qualified_teachers)
                        assignment.teacher_id = new_teacher['id']
                
                elif mutation_type == 'classroom':
                    # 变异教室
                    suitable_classrooms = [c for c in classrooms 
                                         if c.get('is_available', True)]
                    if suitable_classrooms:
                        new_classroom = random.choice(suitable_classrooms)
                        assignment.classroom_id = new_classroom['id']
                
                elif mutation_type == 'time':
                    # 变异时间
                    assignment.day_of_week = random.randint(1, 5)  # 周一到周五
                    assignment.time_slot = random.randint(1, 10)   # 10个时间段
        
        return mutated
    
    @staticmethod
    def swap_mutation(individual: Individual) -> Individual:
        """交换变异 - 交换两个分配的时间"""
        mutated = individual.copy()
        
        if len(mutated.assignments) < 2:
            return mutated
        
        # 随机选择两个分配
        idx1, idx2 = random.sample(range(len(mutated.assignments)), 2)
        assignment1 = mutated.assignments[idx1]
        assignment2 = mutated.assignments[idx2]
        
        # 交换时间信息
        assignment1.day_of_week, assignment2.day_of_week = assignment2.day_of_week, assignment1.day_of_week
        assignment1.time_slot, assignment2.time_slot = assignment2.time_slot, assignment1.time_slot
        
        return mutated
    
    @staticmethod
    def time_shift_mutation(individual: Individual) -> Individual:
        """时间偏移变异 - 将分配移动到相邻时间段"""
        mutated = individual.copy()
        
        if not mutated.assignments:
            return mutated
        
        # 随机选择一个分配
        assignment = random.choice(mutated.assignments)
        
        # 随机选择偏移方向
        if random.random() < 0.5:
            # 时间段偏移
            if assignment.time_slot > 1:
                assignment.time_slot -= 1
            elif assignment.time_slot < 10:
                assignment.time_slot += 1
        else:
            # 星期偏移
            if assignment.day_of_week > 1:
                assignment.day_of_week -= 1
            elif assignment.day_of_week < 5:
                assignment.day_of_week += 1
        
        return mutated
    
    @staticmethod
    def adaptive_mutation(individual: Individual, teachers: List[Dict], 
                         classrooms: List[Dict], generation: int, 
                         max_generations: int) -> Individual:
        """自适应变异 - 根据进化代数调整变异概率"""
        # 计算自适应变异概率
        base_probability = 0.1
        adaptive_factor = 1.0 - (generation / max_generations)
        mutation_probability = base_probability * (1.0 + adaptive_factor)
        
        return MutationOperator.random_mutation(
            individual, teachers, classrooms, mutation_probability
        )
    
    @staticmethod
    def guided_mutation(individual: Individual, teachers: List[Dict], 
                       classrooms: List[Dict], conflicts: List[Any]) -> Individual:
        """引导变异 - 针对冲突进行变异"""
        mutated = individual.copy()
        
        if not conflicts:
            return MutationOperator.random_mutation(mutated, teachers, classrooms)
        
        # 选择一个冲突进行修复
        conflict = random.choice(conflicts)
        
        if conflict.conflict_type in ['teacher_time', 'classroom_time']:
            # 对冲突的分配进行时间变异
            conflicting_assignment = random.choice(conflict.assignments)
            
            for assignment in mutated.assignments:
                if (assignment.course_id == conflicting_assignment.course_id and
                    assignment.teacher_id == conflicting_assignment.teacher_id):
                    # 尝试新的时间段
                    assignment.day_of_week = random.randint(1, 5)
                    assignment.time_slot = random.randint(1, 10)
                    break
        
        return mutated
