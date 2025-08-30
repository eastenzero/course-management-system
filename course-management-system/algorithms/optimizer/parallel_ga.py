# file: algorithms/optimizer/parallel_ga.py
# 功能: 并行遗传算法

import time
import logging
from typing import List, Dict, Any, Optional
from multiprocessing import Pool, Manager, cpu_count
import concurrent.futures
from ..genetic.genetic_algorithm import GeneticAlgorithm
from ..genetic.individual import Individual
from ..models import ScheduleResult

logger = logging.getLogger(__name__)


class ParallelGeneticAlgorithm:
    """并行遗传算法"""
    
    def __init__(self, num_processes: Optional[int] = None,
                 population_size_per_process: int = 50,
                 migration_interval: int = 50,
                 migration_rate: float = 0.1,
                 max_generations: int = 500,
                 **ga_kwargs):
        """
        初始化并行遗传算法
        
        Args:
            num_processes: 并行进程数，默认为CPU核心数
            population_size_per_process: 每个进程的种群大小
            migration_interval: 迁移间隔（代数）
            migration_rate: 迁移率
            max_generations: 最大进化代数
            **ga_kwargs: 传递给GeneticAlgorithm的其他参数
        """
        self.num_processes = num_processes or cpu_count()
        self.population_size_per_process = population_size_per_process
        self.migration_interval = migration_interval
        self.migration_rate = migration_rate
        self.max_generations = max_generations
        self.ga_kwargs = ga_kwargs
        
        # 统计信息
        self.stats = {
            'total_time': 0.0,
            'best_fitness_history': [],
            'process_stats': [],
            'migrations': 0,
            'final_generation': 0,
        }
    
    def evolve(self, courses: List[Dict], teachers: List[Dict], 
              classrooms: List[Dict], teacher_preferences: List[Any] = None) -> ScheduleResult:
        """并行进化"""
        start_time = time.time()
        
        logger.info(f"Starting parallel genetic algorithm with {self.num_processes} processes")
        
        # 使用线程池而不是进程池，避免序列化问题
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_processes) as executor:
            # 为每个线程创建独立的遗传算法实例
            futures = []
            
            for process_id in range(self.num_processes):
                future = executor.submit(
                    self._run_ga_process, 
                    process_id, courses, teachers, classrooms, teacher_preferences
                )
                futures.append(future)
            
            # 收集结果
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Process failed with error: {e}")
        
        # 选择最佳结果
        if results:
            best_result = max(results, key=lambda x: x['best_individual'].fitness)
            best_individual = best_result['best_individual']
            
            # 合并统计信息
            self._merge_statistics(results)
        else:
            # 如果并行失败，使用单线程版本
            logger.warning("Parallel execution failed, falling back to single-threaded")
            return self._fallback_single_thread(courses, teachers, classrooms, teacher_preferences)
        
        self.stats['total_time'] = time.time() - start_time
        
        # 创建结果
        result = ScheduleResult(
            assignments=best_individual.assignments,
            conflicts=best_individual.get_conflicts(),
            fitness_score=best_individual.fitness,
            algorithm_used='parallel_genetic',
            generation_time=self.stats['total_time'],
            metadata={
                'num_processes': self.num_processes,
                'population_size_per_process': self.population_size_per_process,
                'stats': self.stats.copy(),
            }
        )
        
        logger.info(f"Parallel genetic algorithm completed: "
                   f"best fitness = {best_individual.fitness:.2f}, "
                   f"time = {self.stats['total_time']:.2f}s")
        
        return result
    
    def _run_ga_process(self, process_id: int, courses: List[Dict], 
                       teachers: List[Dict], classrooms: List[Dict],
                       teacher_preferences: List[Any] = None) -> Dict[str, Any]:
        """运行单个遗传算法进程"""
        logger.debug(f"Starting GA process {process_id}")
        
        # 创建遗传算法实例
        ga = GeneticAlgorithm(
            population_size=self.population_size_per_process,
            max_generations=self.max_generations,
            **self.ga_kwargs
        )
        
        # 设置数据
        ga.set_data(courses, teachers, classrooms, teacher_preferences)
        
        # 运行进化
        best_individual = ga.evolve()
        
        # 返回结果
        return {
            'process_id': process_id,
            'best_individual': best_individual,
            'stats': ga.get_statistics(),
        }
    
    def _merge_statistics(self, results: List[Dict[str, Any]]):
        """合并统计信息"""
        self.stats['process_stats'] = []
        all_fitness_histories = []
        
        for result in results:
            process_stats = result['stats']
            self.stats['process_stats'].append({
                'process_id': result['process_id'],
                'best_fitness': process_stats['best_fitness'],
                'final_generation': process_stats['final_generation'],
                'total_evaluations': process_stats['total_evaluations'],
            })
            
            # 收集适应度历史
            if 'best_fitness_history' in process_stats:
                all_fitness_histories.append(process_stats['best_fitness_history'])
        
        # 计算全局最佳适应度历史
        if all_fitness_histories:
            max_length = max(len(history) for history in all_fitness_histories)
            global_best_history = []
            
            for generation in range(max_length):
                generation_best = float('-inf')
                for history in all_fitness_histories:
                    if generation < len(history):
                        generation_best = max(generation_best, history[generation])
                global_best_history.append(generation_best)
            
            self.stats['best_fitness_history'] = global_best_history
        
        # 计算总体统计
        if self.stats['process_stats']:
            self.stats['final_generation'] = max(
                p['final_generation'] for p in self.stats['process_stats']
            )
    
    def _fallback_single_thread(self, courses: List[Dict], teachers: List[Dict],
                               classrooms: List[Dict], teacher_preferences: List[Any] = None) -> ScheduleResult:
        """单线程回退方案"""
        ga = GeneticAlgorithm(
            population_size=self.population_size_per_process * self.num_processes,
            max_generations=self.max_generations,
            **self.ga_kwargs
        )
        
        ga.set_data(courses, teachers, classrooms, teacher_preferences)
        best_individual = ga.evolve()
        
        return ScheduleResult(
            assignments=best_individual.assignments,
            conflicts=best_individual.get_conflicts(),
            fitness_score=best_individual.fitness,
            algorithm_used='genetic_fallback',
            generation_time=ga.get_statistics()['total_time'],
            metadata={
                'fallback': True,
                'stats': ga.get_statistics(),
            }
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()


class IslandGeneticAlgorithm:
    """岛屿遗传算法 - 带迁移的并行GA"""
    
    def __init__(self, num_islands: int = 4,
                 population_size_per_island: int = 50,
                 migration_interval: int = 25,
                 migration_size: int = 5,
                 topology: str = 'ring',
                 **ga_kwargs):
        """
        初始化岛屿遗传算法
        
        Args:
            num_islands: 岛屿数量
            population_size_per_island: 每个岛屿的种群大小
            migration_interval: 迁移间隔
            migration_size: 迁移个体数量
            topology: 拓扑结构 ('ring', 'star', 'complete')
            **ga_kwargs: 遗传算法参数
        """
        self.num_islands = num_islands
        self.population_size_per_island = population_size_per_island
        self.migration_interval = migration_interval
        self.migration_size = migration_size
        self.topology = topology
        self.ga_kwargs = ga_kwargs
        
        # 创建岛屿间的连接拓扑
        self.migration_topology = self._create_migration_topology()
        
        # 统计信息
        self.stats = {
            'total_time': 0.0,
            'migrations_performed': 0,
            'island_stats': [],
            'global_best_history': [],
        }
    
    def _create_migration_topology(self) -> Dict[int, List[int]]:
        """创建迁移拓扑"""
        topology = {}
        
        if self.topology == 'ring':
            # 环形拓扑
            for i in range(self.num_islands):
                next_island = (i + 1) % self.num_islands
                topology[i] = [next_island]
        
        elif self.topology == 'star':
            # 星形拓扑（岛屿0为中心）
            topology[0] = list(range(1, self.num_islands))
            for i in range(1, self.num_islands):
                topology[i] = [0]
        
        elif self.topology == 'complete':
            # 完全连接拓扑
            for i in range(self.num_islands):
                topology[i] = [j for j in range(self.num_islands) if j != i]
        
        return topology
    
    def evolve(self, courses: List[Dict], teachers: List[Dict],
              classrooms: List[Dict], teacher_preferences: List[Any] = None) -> ScheduleResult:
        """岛屿进化"""
        start_time = time.time()
        
        logger.info(f"Starting island genetic algorithm with {self.num_islands} islands")
        
        # 初始化岛屿
        islands = []
        for i in range(self.num_islands):
            ga = GeneticAlgorithm(
                population_size=self.population_size_per_island,
                **self.ga_kwargs
            )
            ga.set_data(courses, teachers, classrooms, teacher_preferences)
            islands.append(ga)
        
        # 进化循环
        global_best_individual = None
        global_best_fitness = float('-inf')
        
        max_generations = self.ga_kwargs.get('max_generations', 1000)
        
        for generation in range(max_generations):
            # 每个岛屿进化一代
            for island in islands:
                island.current_generation = generation
                # 这里需要实现单代进化，暂时跳过
                pass
            
            # 迁移操作
            if generation % self.migration_interval == 0 and generation > 0:
                self._perform_migration(islands)
                self.stats['migrations_performed'] += 1
            
            # 更新全局最佳
            for island in islands:
                if island.best_individual and island.best_individual.fitness > global_best_fitness:
                    global_best_fitness = island.best_individual.fitness
                    global_best_individual = island.best_individual.copy()
            
            self.stats['global_best_history'].append(global_best_fitness)
            
            # 定期输出进度
            if generation % 100 == 0:
                logger.info(f"Generation {generation}: Global best fitness = {global_best_fitness:.2f}")
        
        self.stats['total_time'] = time.time() - start_time
        
        # 收集岛屿统计信息
        for i, island in enumerate(islands):
            self.stats['island_stats'].append({
                'island_id': i,
                'best_fitness': island.best_individual.fitness if island.best_individual else 0,
                'stats': island.get_statistics(),
            })
        
        # 创建结果
        result = ScheduleResult(
            assignments=global_best_individual.assignments if global_best_individual else [],
            conflicts=global_best_individual.get_conflicts() if global_best_individual else [],
            fitness_score=global_best_fitness,
            algorithm_used='island_genetic',
            generation_time=self.stats['total_time'],
            metadata={
                'num_islands': self.num_islands,
                'topology': self.topology,
                'migrations_performed': self.stats['migrations_performed'],
                'stats': self.stats.copy(),
            }
        )
        
        logger.info(f"Island genetic algorithm completed: "
                   f"best fitness = {global_best_fitness:.2f}, "
                   f"migrations = {self.stats['migrations_performed']}")
        
        return result
    
    def _perform_migration(self, islands: List[GeneticAlgorithm]):
        """执行迁移操作"""
        # 收集每个岛屿的最佳个体
        migrants = {}
        for i, island in enumerate(islands):
            if island.best_individual:
                # 选择要迁移的个体（这里简化为最佳个体）
                migrants[i] = [island.best_individual.copy() for _ in range(self.migration_size)]
        
        # 根据拓扑结构进行迁移
        for source_island, target_islands in self.migration_topology.items():
            if source_island in migrants:
                for target_island in target_islands:
                    if target_island < len(islands):
                        # 将迁移个体添加到目标岛屿
                        # 这里需要实现将个体添加到种群的逻辑
                        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
