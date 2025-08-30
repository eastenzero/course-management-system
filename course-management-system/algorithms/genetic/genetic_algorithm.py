# file: algorithms/genetic/genetic_algorithm.py
# 功能: 遗传算法排课器主类

import random
import time
import logging
from typing import List, Dict, Any, Optional, Callable
import numpy as np
from .individual import Individual
from .operators import SelectionOperator, CrossoverOperator, MutationOperator
from ..models import Assignment
from ..constraints.manager import ConstraintManager

logger = logging.getLogger(__name__)


class GeneticAlgorithm:
    """遗传算法排课器"""
    
    def __init__(self, 
                 population_size: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 elite_rate: float = 0.1,
                 max_generations: int = 1000,
                 convergence_threshold: int = 50,
                 selection_method: str = 'tournament',
                 crossover_method: str = 'course_based',
                 mutation_method: str = 'adaptive',
                 constraint_manager: Optional[ConstraintManager] = None):
        """
        初始化遗传算法
        
        Args:
            population_size: 种群大小
            mutation_rate: 变异率
            crossover_rate: 交叉率
            elite_rate: 精英保留率
            max_generations: 最大进化代数
            convergence_threshold: 收敛阈值（多少代无改进则停止）
            selection_method: 选择方法 ('tournament', 'roulette', 'rank')
            crossover_method: 交叉方法 ('single_point', 'two_point', 'uniform', 'course_based')
            mutation_method: 变异方法 ('random', 'swap', 'time_shift', 'adaptive', 'guided')
            constraint_manager: 约束管理器
        """
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_rate = elite_rate
        self.max_generations = max_generations
        self.convergence_threshold = convergence_threshold
        
        self.selection_method = selection_method
        self.crossover_method = crossover_method
        self.mutation_method = mutation_method
        
        self.constraint_manager = constraint_manager or ConstraintManager()
        
        # 算法状态
        self.current_generation = 0
        self.best_individual = None
        self.best_fitness_history = []
        self.average_fitness_history = []
        self.convergence_counter = 0
        
        # 统计信息
        self.stats = {
            'total_evaluations': 0,
            'total_time': 0.0,
            'best_fitness': float('-inf'),
            'final_generation': 0,
            'convergence_reason': '',
        }
        
        # 回调函数
        self.generation_callback: Optional[Callable] = None
        self.improvement_callback: Optional[Callable] = None
    
    def set_data(self, courses: List[Dict], teachers: List[Dict], 
                classrooms: List[Dict], teacher_preferences: List[Any] = None):
        """设置算法所需的数据"""
        self.courses = courses
        self.teachers = teachers
        self.classrooms = classrooms
        
        # 设置约束管理器的数据缓存
        self.constraint_manager.set_data_cache(
            courses, teachers, classrooms, teacher_preferences
        )
        
        logger.info(f"Data set: {len(courses)} courses, {len(teachers)} teachers, {len(classrooms)} classrooms")
    
    def initialize_population(self) -> List[Individual]:
        """初始化种群"""
        population = []
        
        logger.info(f"Initializing population of size {self.population_size}")
        
        for i in range(self.population_size):
            individual = self._create_random_individual()
            population.append(individual)
            
            if (i + 1) % 20 == 0:
                logger.debug(f"Created {i + 1}/{self.population_size} individuals")
        
        return population
    
    def _create_random_individual(self) -> Individual:
        """创建随机个体"""
        assignments = []
        
        for course in self.courses:
            # 为每门课程随机分配教师、教室和时间
            qualified_teachers = [t for t in self.teachers 
                                if course['id'] in t.get('qualified_courses', [])]
            if not qualified_teachers:
                qualified_teachers = self.teachers  # 如果没有合格教师，使用所有教师
            
            suitable_classrooms = [c for c in self.classrooms 
                                 if c.get('capacity', 0) >= course.get('max_students', 0)]
            if not suitable_classrooms:
                suitable_classrooms = self.classrooms  # 如果没有合适教室，使用所有教室
            
            teacher = random.choice(qualified_teachers)
            classroom = random.choice(suitable_classrooms)
            
            # 随机选择时间段
            day_of_week = random.randint(1, 5)  # 周一到周五
            time_slot = random.randint(1, 10)   # 10个时间段
            
            assignment = Assignment(
                course_id=course['id'],
                teacher_id=teacher['id'],
                classroom_id=classroom['id'],
                day_of_week=day_of_week,
                time_slot=time_slot,
                semester=course.get('semester', ''),
                academic_year=course.get('academic_year', ''),
            )
            assignments.append(assignment)
        
        return Individual(assignments=assignments)
    
    def evaluate_population(self, population: List[Individual]) -> List[Individual]:
        """评估种群中所有个体的适应度"""
        for individual in population:
            if not individual._evaluated:
                individual.calculate_fitness(self.constraint_manager)
                self.stats['total_evaluations'] += 1
        
        return population
    
    def selection(self, population: List[Individual]) -> List[Individual]:
        """选择操作"""
        selected = []
        
        for _ in range(len(population)):
            if self.selection_method == 'tournament':
                individual = SelectionOperator.tournament_selection(population)
            elif self.selection_method == 'roulette':
                individual = SelectionOperator.roulette_wheel_selection(population)
            elif self.selection_method == 'rank':
                individual = SelectionOperator.rank_selection(population)
            else:
                individual = SelectionOperator.tournament_selection(population)
            
            selected.append(individual)
        
        return selected
    
    def crossover(self, parent1: Individual, parent2: Individual) -> tuple[Individual, Individual]:
        """交叉操作"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        if self.crossover_method == 'single_point':
            return CrossoverOperator.single_point_crossover(parent1, parent2)
        elif self.crossover_method == 'two_point':
            return CrossoverOperator.two_point_crossover(parent1, parent2)
        elif self.crossover_method == 'uniform':
            return CrossoverOperator.uniform_crossover(parent1, parent2)
        elif self.crossover_method == 'course_based':
            return CrossoverOperator.course_based_crossover(parent1, parent2)
        else:
            return CrossoverOperator.course_based_crossover(parent1, parent2)
    
    def mutation(self, individual: Individual) -> Individual:
        """变异操作"""
        if random.random() > self.mutation_rate:
            return individual
        
        if self.mutation_method == 'random':
            return MutationOperator.random_mutation(individual, self.teachers, self.classrooms)
        elif self.mutation_method == 'swap':
            return MutationOperator.swap_mutation(individual)
        elif self.mutation_method == 'time_shift':
            return MutationOperator.time_shift_mutation(individual)
        elif self.mutation_method == 'adaptive':
            return MutationOperator.adaptive_mutation(
                individual, self.teachers, self.classrooms, 
                self.current_generation, self.max_generations
            )
        elif self.mutation_method == 'guided':
            conflicts = individual.get_conflicts()
            return MutationOperator.guided_mutation(
                individual, self.teachers, self.classrooms, conflicts
            )
        else:
            return MutationOperator.adaptive_mutation(
                individual, self.teachers, self.classrooms,
                self.current_generation, self.max_generations
            )
    
    def evolve_generation(self, population: List[Individual]) -> List[Individual]:
        """进化一代"""
        # 评估当前种群
        population = self.evaluate_population(population)
        
        # 精英保留
        elite_size = int(self.population_size * self.elite_rate)
        elite = SelectionOperator.elite_selection(population, elite_size)
        
        # 选择
        selected = self.selection(population)
        
        # 交叉和变异生成新个体
        new_population = elite.copy()
        
        while len(new_population) < self.population_size:
            # 选择父代
            parent1 = random.choice(selected)
            parent2 = random.choice(selected)
            
            # 交叉
            child1, child2 = self.crossover(parent1, parent2)
            
            # 变异
            child1 = self.mutation(child1)
            child2 = self.mutation(child2)
            
            new_population.extend([child1, child2])
        
        # 确保种群大小
        new_population = new_population[:self.population_size]
        
        return new_population

    def evolve(self) -> Individual:
        """主进化过程"""
        if not hasattr(self, 'courses'):
            raise ValueError("Data not set. Call set_data() first.")

        start_time = time.time()
        logger.info(f"Starting genetic algorithm evolution")

        # 初始化种群
        population = self.initialize_population()
        population = self.evaluate_population(population)

        # 记录初始最佳个体
        self.best_individual = max(population, key=lambda x: x.fitness)
        self.best_fitness_history.append(self.best_individual.fitness)
        self.stats['best_fitness'] = self.best_individual.fitness

        logger.info(f"Initial best fitness: {self.best_individual.fitness:.2f}")

        # 进化循环
        for generation in range(self.max_generations):
            self.current_generation = generation

            # 进化一代
            population = self.evolve_generation(population)

            # 更新最佳个体
            current_best = max(population, key=lambda x: x.fitness)
            if current_best.fitness > self.best_individual.fitness:
                self.best_individual = current_best.copy()
                self.stats['best_fitness'] = self.best_individual.fitness
                self.convergence_counter = 0

                if self.improvement_callback:
                    self.improvement_callback(self.best_individual, generation)

                logger.info(f"Generation {generation}: New best fitness {self.best_individual.fitness:.2f}")
            else:
                self.convergence_counter += 1

            # 记录统计信息
            average_fitness = sum(ind.fitness for ind in population) / len(population)
            self.best_fitness_history.append(self.best_individual.fitness)
            self.average_fitness_history.append(average_fitness)

            # 调用回调函数
            if self.generation_callback:
                self.generation_callback(population, generation)

            # 检查收敛条件
            if self.convergence_counter >= self.convergence_threshold:
                self.stats['convergence_reason'] = f'No improvement for {self.convergence_threshold} generations'
                logger.info(f"Converged at generation {generation}: {self.stats['convergence_reason']}")
                break

            # 检查是否找到完美解
            if self.best_individual.is_valid() and self.best_individual.fitness >= 95:
                self.stats['convergence_reason'] = 'Found near-optimal solution'
                logger.info(f"Found excellent solution at generation {generation}")
                break

            # 定期输出进度
            if generation % 100 == 0:
                logger.info(f"Generation {generation}: Best={self.best_individual.fitness:.2f}, "
                          f"Avg={average_fitness:.2f}, Valid={self.best_individual.is_valid()}")

        # 记录最终统计信息
        self.stats['total_time'] = time.time() - start_time
        self.stats['final_generation'] = self.current_generation

        if not self.stats['convergence_reason']:
            self.stats['convergence_reason'] = 'Reached maximum generations'

        logger.info(f"Evolution completed: {self.stats['convergence_reason']}")
        logger.info(f"Final best fitness: {self.best_individual.fitness:.2f}")
        logger.info(f"Total time: {self.stats['total_time']:.2f} seconds")
        logger.info(f"Total evaluations: {self.stats['total_evaluations']}")

        return self.best_individual

    def evolve_with_seed(self, seed_individual: Individual) -> Individual:
        """使用种子个体进行进化"""
        if not hasattr(self, 'courses'):
            raise ValueError("Data not set. Call set_data() first.")

        # 初始化种群，包含种子个体
        population = [seed_individual.copy()]

        # 生成其余个体
        for _ in range(self.population_size - 1):
            individual = self._create_random_individual()
            population.append(individual)

        # 设置种群并开始进化
        self.best_individual = seed_individual.copy()
        return self._evolve_with_population(population)

    def _evolve_with_population(self, initial_population: List[Individual]) -> Individual:
        """使用给定的初始种群进行进化"""
        start_time = time.time()
        population = initial_population

        # 评估初始种群
        population = self.evaluate_population(population)

        # 更新最佳个体
        current_best = max(population, key=lambda x: x.fitness)
        if current_best.fitness > self.best_individual.fitness:
            self.best_individual = current_best.copy()

        self.best_fitness_history.append(self.best_individual.fitness)

        # 进化循环（与evolve方法类似）
        for generation in range(self.max_generations):
            self.current_generation = generation
            population = self.evolve_generation(population)

            current_best = max(population, key=lambda x: x.fitness)
            if current_best.fitness > self.best_individual.fitness:
                self.best_individual = current_best.copy()
                self.convergence_counter = 0
            else:
                self.convergence_counter += 1

            average_fitness = sum(ind.fitness for ind in population) / len(population)
            self.best_fitness_history.append(self.best_individual.fitness)
            self.average_fitness_history.append(average_fitness)

            if self.convergence_counter >= self.convergence_threshold:
                break

            if self.best_individual.is_valid() and self.best_individual.fitness >= 95:
                break

        self.stats['total_time'] = time.time() - start_time
        self.stats['final_generation'] = self.current_generation

        return self.best_individual

    def get_statistics(self) -> Dict[str, Any]:
        """获取算法运行统计信息"""
        return {
            'total_evaluations': self.stats['total_evaluations'],
            'total_time': self.stats['total_time'],
            'final_generation': self.stats['final_generation'],
            'convergence_reason': self.stats['convergence_reason'],
            'best_fitness': self.stats['best_fitness'],
            'best_fitness_history': self.best_fitness_history.copy(),
            'average_fitness_history': self.average_fitness_history.copy(),
            'population_size': self.population_size,
            'mutation_rate': self.mutation_rate,
            'crossover_rate': self.crossover_rate,
            'elite_rate': self.elite_rate,
            'selection_method': self.selection_method,
            'crossover_method': self.crossover_method,
            'mutation_method': self.mutation_method,
        }

    def set_callbacks(self, generation_callback: Callable = None,
                     improvement_callback: Callable = None):
        """设置回调函数"""
        self.generation_callback = generation_callback
        self.improvement_callback = improvement_callback

    def reset(self):
        """重置算法状态"""
        self.current_generation = 0
        self.best_individual = None
        self.best_fitness_history = []
        self.average_fitness_history = []
        self.convergence_counter = 0

        self.stats = {
            'total_evaluations': 0,
            'total_time': 0.0,
            'best_fitness': float('-inf'),
            'final_generation': 0,
            'convergence_reason': '',
        }

        # 重置约束管理器统计
        self.constraint_manager.reset_statistics()

    def update_parameters(self, **kwargs):
        """动态更新算法参数"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.info(f"Updated parameter {key} to {value}")
            else:
                logger.warning(f"Unknown parameter: {key}")

    def export_best_solution(self) -> Dict[str, Any]:
        """导出最佳解决方案"""
        if not self.best_individual:
            return {}

        return {
            'assignments': [a.to_dict() for a in self.best_individual.assignments],
            'fitness': self.best_individual.fitness,
            'hard_violations': self.best_individual.hard_violations,
            'soft_score': self.best_individual.soft_score,
            'is_valid': self.best_individual.is_valid(),
            'conflicts': [c.to_dict() for c in self.best_individual.get_conflicts()],
            'statistics': self.get_statistics(),
        }

    def import_solution(self, solution_data: Dict[str, Any]) -> Individual:
        """导入解决方案"""
        assignments = [Assignment.from_dict(a) for a in solution_data['assignments']]
        individual = Individual(assignments=assignments)
        individual.fitness = solution_data.get('fitness', 0.0)
        individual.hard_violations = solution_data.get('hard_violations', 0)
        individual.soft_score = solution_data.get('soft_score', 0.0)
        return individual

    def validate_configuration(self) -> List[str]:
        """验证算法配置"""
        errors = []

        if self.population_size < 10:
            errors.append("Population size should be at least 10")

        if not (0.0 <= self.mutation_rate <= 1.0):
            errors.append("Mutation rate should be between 0.0 and 1.0")

        if not (0.0 <= self.crossover_rate <= 1.0):
            errors.append("Crossover rate should be between 0.0 and 1.0")

        if not (0.0 <= self.elite_rate <= 1.0):
            errors.append("Elite rate should be between 0.0 and 1.0")

        if self.max_generations < 1:
            errors.append("Max generations should be at least 1")

        if self.convergence_threshold < 1:
            errors.append("Convergence threshold should be at least 1")

        valid_selection_methods = ['tournament', 'roulette', 'rank']
        if self.selection_method not in valid_selection_methods:
            errors.append(f"Selection method should be one of {valid_selection_methods}")

        valid_crossover_methods = ['single_point', 'two_point', 'uniform', 'course_based']
        if self.crossover_method not in valid_crossover_methods:
            errors.append(f"Crossover method should be one of {valid_crossover_methods}")

        valid_mutation_methods = ['random', 'swap', 'time_shift', 'adaptive', 'guided']
        if self.mutation_method not in valid_mutation_methods:
            errors.append(f"Mutation method should be one of {valid_mutation_methods}")

        return errors
