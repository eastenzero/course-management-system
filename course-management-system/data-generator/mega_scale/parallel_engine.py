# file: data-generator/mega_scale/parallel_engine.py
# 功能: 并行计算引擎和任务分配系统

import multiprocessing as mp
import threading
import time
import queue
import psutil
from typing import Any, Dict, List, Optional, Callable, Tuple, Union
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from pathlib import Path
import pickle
import json


@dataclass
class TaskConfig:
    """任务配置"""
    task_id: str
    task_type: str                    # 任务类型
    priority: int = 5                 # 优先级 (1-10, 1最高)
    estimated_duration: float = 60.0  # 预估耗时(秒)
    memory_requirement_mb: int = 100   # 内存需求(MB)
    cpu_intensive: bool = True         # 是否CPU密集型
    dependencies: List[str] = field(default_factory=list)  # 依赖任务ID


@dataclass
class WorkerConfig:
    """工作进程配置"""
    worker_id: str
    process_type: str = "process"     # process 或 thread
    max_tasks: int = 100             # 最大任务数
    max_memory_mb: int = 512         # 最大内存限制
    timeout_seconds: int = 3600      # 超时时间


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    success: bool
    result: Any = None
    error: str = ""
    processing_time: float = 0.0
    memory_used_mb: float = 0.0
    worker_id: str = ""


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, workers: List[WorkerConfig]):
        self.workers = {w.worker_id: w for w in workers}
        self.worker_loads: Dict[str, float] = {w.worker_id: 0.0 for w in workers}
        self.worker_task_counts: Dict[str, int] = {w.worker_id: 0 for w in workers}
        self.lock = threading.Lock()
    
    def select_worker(self, task: TaskConfig) -> Optional[str]:
        """选择最合适的工作进程"""
        with self.lock:
            # 过滤可用的工作进程
            available_workers = []
            
            for worker_id, worker_config in self.workers.items():
                # 检查内存要求
                if task.memory_requirement_mb <= worker_config.max_memory_mb:
                    # 检查任务数限制
                    if self.worker_task_counts[worker_id] < worker_config.max_tasks:
                        load = self.worker_loads[worker_id]
                        task_count = self.worker_task_counts[worker_id]
                        
                        # 计算负载分数 (越小越好)
                        load_score = load + (task_count * 0.1)
                        available_workers.append((worker_id, load_score))
            
            if not available_workers:
                return None
            
            # 选择负载最小的工作进程
            selected_worker = min(available_workers, key=lambda x: x[1])[0]
            
            # 更新负载信息
            self.worker_loads[selected_worker] += task.estimated_duration
            self.worker_task_counts[selected_worker] += 1
            
            return selected_worker
    
    def update_worker_completion(self, worker_id: str, actual_duration: float):
        """更新工作进程完成情况"""
        with self.lock:
            if worker_id in self.worker_loads:
                self.worker_loads[worker_id] = max(0, 
                    self.worker_loads[worker_id] - actual_duration)
                self.worker_task_counts[worker_id] = max(0,
                    self.worker_task_counts[worker_id] - 1)
    
    def get_load_summary(self) -> Dict[str, Any]:
        """获取负载摘要"""
        with self.lock:
            return {
                'workers': dict(self.workers),
                'loads': dict(self.worker_loads),
                'task_counts': dict(self.worker_task_counts),
                'total_load': sum(self.worker_loads.values()),
                'total_tasks': sum(self.worker_task_counts.values())
            }


class TaskQueue:
    """任务队列管理器"""
    
    def __init__(self):
        self.pending_tasks: Dict[int, List[TaskConfig]] = {}  # 按优先级分组
        self.running_tasks: Dict[str, TaskConfig] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.failed_tasks: Dict[str, TaskResult] = {}
        self.task_dependencies: Dict[str, List[str]] = {}
        self.lock = threading.Lock()
    
    def add_task(self, task: TaskConfig):
        """添加任务"""
        with self.lock:
            if task.priority not in self.pending_tasks:
                self.pending_tasks[task.priority] = []
            
            self.pending_tasks[task.priority].append(task)
            
            # 记录依赖关系
            if task.dependencies:
                self.task_dependencies[task.task_id] = task.dependencies
    
    def get_next_task(self) -> Optional[TaskConfig]:
        """获取下一个可执行任务"""
        with self.lock:
            # 按优先级从高到低遍历
            for priority in sorted(self.pending_tasks.keys()):
                tasks = self.pending_tasks[priority]
                
                for i, task in enumerate(tasks):
                    # 检查依赖是否满足
                    if self._are_dependencies_satisfied(task.task_id):
                        # 移除并返回任务
                        tasks.pop(i)
                        if not tasks:
                            del self.pending_tasks[priority]
                        
                        self.running_tasks[task.task_id] = task
                        return task
            
            return None
    
    def _are_dependencies_satisfied(self, task_id: str) -> bool:
        """检查任务依赖是否满足"""
        dependencies = self.task_dependencies.get(task_id, [])
        
        for dep_id in dependencies:
            if dep_id not in self.completed_tasks:
                return False
        
        return True
    
    def complete_task(self, result: TaskResult):
        """完成任务"""
        with self.lock:
            task_id = result.task_id
            
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            if result.success:
                self.completed_tasks[task_id] = result
            else:
                self.failed_tasks[task_id] = result
    
    def get_status(self) -> Dict[str, int]:
        """获取队列状态"""
        with self.lock:
            pending_count = sum(len(tasks) for tasks in self.pending_tasks.values())
            
            return {
                'pending': pending_count,
                'running': len(self.running_tasks),
                'completed': len(self.completed_tasks),
                'failed': len(self.failed_tasks),
                'total': pending_count + len(self.running_tasks) + 
                        len(self.completed_tasks) + len(self.failed_tasks)
            }


class WorkerProcess:
    """工作进程"""
    
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.process = psutil.Process()
        self.current_task: Optional[TaskConfig] = None
        self.start_time: Optional[float] = None
        self.task_count = 0
        self.total_processing_time = 0.0
    
    @staticmethod
    def execute_task(task_config: TaskConfig, task_func: Callable, 
                    task_args: Tuple, task_kwargs: Dict) -> TaskResult:
        """执行任务（静态方法，用于多进程）"""
        start_time = time.time()
        worker_id = mp.current_process().name
        
        try:
            # 执行任务
            result = task_func(*task_args, **task_kwargs)
            
            processing_time = time.time() - start_time
            
            # 获取内存使用量
            process = psutil.Process()
            memory_used_mb = process.memory_info().rss / 1024 / 1024
            
            return TaskResult(
                task_id=task_config.task_id,
                success=True,
                result=result,
                processing_time=processing_time,
                memory_used_mb=memory_used_mb,
                worker_id=worker_id
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return TaskResult(
                task_id=task_config.task_id,
                success=False,
                error=str(e),
                processing_time=processing_time,
                worker_id=worker_id
            )


class ParallelComputingEngine:
    """并行计算引擎"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (psutil.cpu_count() or 1) + 4)
        self.task_queue = TaskQueue()
        self.load_balancer: Optional[LoadBalancer] = None
        self.process_executor: Optional[ProcessPoolExecutor] = None
        self.thread_executor: Optional[ThreadPoolExecutor] = None
        
        # 任务注册表
        self.task_functions: Dict[str, Callable] = {}
        self.task_args: Dict[str, Tuple] = {}
        self.task_kwargs: Dict[str, Dict] = {}
        
        # 运行状态
        self.running = False
        self.coordinator_thread: Optional[threading.Thread] = None
        
        # 统计信息
        self.start_time: Optional[float] = None
        self.total_tasks_processed = 0
        self.total_processing_time = 0.0
    
    def register_task_function(self, task_type: str, func: Callable):
        """注册任务处理函数"""
        self.task_functions[task_type] = func
    
    def initialize_workers(self, process_workers: int = None, thread_workers: int = None):
        """初始化工作进程和线程"""
        if process_workers is None:
            process_workers = max(1, self.max_workers // 2)
        if thread_workers is None:
            thread_workers = max(1, self.max_workers - process_workers)
        
        # 创建工作进程配置
        worker_configs = []
        
        for i in range(process_workers):
            config = WorkerConfig(
                worker_id=f"process_{i}",
                process_type="process",
                max_memory_mb=512
            )
            worker_configs.append(config)
        
        for i in range(thread_workers):
            config = WorkerConfig(
                worker_id=f"thread_{i}",
                process_type="thread",
                max_memory_mb=256
            )
            worker_configs.append(config)
        
        # 初始化负载均衡器
        self.load_balancer = LoadBalancer(worker_configs)
        
        # 创建执行器
        self.process_executor = ProcessPoolExecutor(max_workers=process_workers)
        self.thread_executor = ThreadPoolExecutor(max_workers=thread_workers)
        
        print(f"🚀 初始化并行引擎: {process_workers}进程 + {thread_workers}线程")
    
    def submit_task(self, task_config: TaskConfig, func: Callable, 
                   *args, **kwargs) -> str:
        """提交任务"""
        # 注册任务函数和参数
        self.task_functions[task_config.task_id] = func
        self.task_args[task_config.task_id] = args
        self.task_kwargs[task_config.task_id] = kwargs
        
        # 添加到任务队列
        self.task_queue.add_task(task_config)
        
        return task_config.task_id
    
    def submit_batch_tasks(self, tasks: List[Tuple[TaskConfig, Callable, Tuple, Dict]]) -> List[str]:
        """批量提交任务"""
        task_ids = []
        
        for task_config, func, args, kwargs in tasks:
            task_id = self.submit_task(task_config, func, *args, **kwargs)
            task_ids.append(task_id)
        
        return task_ids
    
    def start_processing(self):
        """开始处理任务"""
        if self.running:
            return
        
        self.running = True
        self.start_time = time.time()
        
        # 启动任务协调线程
        self.coordinator_thread = threading.Thread(target=self._task_coordinator, daemon=True)
        self.coordinator_thread.start()
        
        print("📊 并行引擎开始处理任务...")
    
    def _task_coordinator(self):
        """任务协调器（主控制循环）"""
        futures_to_tasks: Dict[Future, TaskConfig] = {}
        
        while self.running:
            try:
                # 检查是否有可执行的任务
                task = self.task_queue.get_next_task()
                
                if task:
                    # 选择工作进程
                    worker_id = self.load_balancer.select_worker(task)
                    
                    if worker_id:
                        # 提交任务到相应的执行器
                        if worker_id.startswith("process_"):
                            future = self.process_executor.submit(
                                WorkerProcess.execute_task,
                                task,
                                self.task_functions[task.task_id],
                                self.task_args[task.task_id],
                                self.task_kwargs[task.task_id]
                            )
                        else:  # thread worker
                            future = self.thread_executor.submit(
                                WorkerProcess.execute_task,
                                task,
                                self.task_functions[task.task_id],
                                self.task_args[task.task_id],
                                self.task_kwargs[task.task_id]
                            )
                        
                        futures_to_tasks[future] = task
                
                # 检查完成的任务
                completed_futures = []
                for future in list(futures_to_tasks.keys()):
                    if future.done():
                        completed_futures.append(future)
                
                for future in completed_futures:
                    task = futures_to_tasks.pop(future)
                    
                    try:
                        result = future.result()
                        
                        # 更新负载均衡器
                        self.load_balancer.update_worker_completion(
                            result.worker_id, result.processing_time
                        )
                        
                        # 完成任务
                        self.task_queue.complete_task(result)
                        
                        # 更新统计
                        self.total_tasks_processed += 1
                        self.total_processing_time += result.processing_time
                        
                        # 清理任务数据
                        self._cleanup_task_data(task.task_id)
                        
                    except Exception as e:
                        print(f"❌ 任务执行异常: {e}")
                        
                        # 创建失败结果
                        failed_result = TaskResult(
                            task_id=task.task_id,
                            success=False,
                            error=str(e)
                        )
                        self.task_queue.complete_task(failed_result)
                
                # 检查是否所有任务都完成
                status = self.task_queue.get_status()
                if status['pending'] == 0 and status['running'] == 0:
                    # 所有任务完成，但保持运行状态等待新任务
                    time.sleep(0.1)
                else:
                    time.sleep(0.01)  # 短暂休眠
                    
            except Exception as e:
                print(f"任务协调器异常: {e}")
                time.sleep(1)
    
    def _cleanup_task_data(self, task_id: str):
        """清理任务数据"""
        if task_id in self.task_functions:
            del self.task_functions[task_id]
        if task_id in self.task_args:
            del self.task_args[task_id]
        if task_id in self.task_kwargs:
            del self.task_kwargs[task_id]
    
    def wait_for_completion(self, timeout: float = None) -> bool:
        """等待所有任务完成"""
        start_wait = time.time()
        
        while True:
            status = self.task_queue.get_status()
            
            if status['pending'] == 0 and status['running'] == 0:
                return True
            
            if timeout and (time.time() - start_wait) > timeout:
                return False
            
            time.sleep(1)
    
    def get_results(self) -> Dict[str, TaskResult]:
        """获取所有完成的任务结果"""
        return dict(self.task_queue.completed_tasks)
    
    def get_failed_results(self) -> Dict[str, TaskResult]:
        """获取所有失败的任务结果"""
        return dict(self.task_queue.failed_tasks)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        elapsed_time = time.time() - (self.start_time or time.time())
        
        stats = {
            'total_tasks_processed': self.total_tasks_processed,
            'total_processing_time': self.total_processing_time,
            'elapsed_time': elapsed_time,
            'tasks_per_second': self.total_tasks_processed / max(elapsed_time, 1),
            'avg_task_time': self.total_processing_time / max(self.total_tasks_processed, 1),
            'parallel_efficiency': (self.total_processing_time / (elapsed_time * self.max_workers)) * 100 if elapsed_time > 0 else 0,
            'queue_status': self.task_queue.get_status()
        }
        
        if self.load_balancer:
            stats['load_balancer'] = self.load_balancer.get_load_summary()
        
        return stats
    
    def stop(self):
        """停止处理"""
        self.running = False
        
        # 等待协调线程结束
        if self.coordinator_thread and self.coordinator_thread.is_alive():
            self.coordinator_thread.join(timeout=5)
        
        # 关闭执行器
        if self.process_executor:
            self.process_executor.shutdown(wait=True)
        if self.thread_executor:
            self.thread_executor.shutdown(wait=True)
        
        print("🛑 并行引擎已停止")


class ResultMerger:
    """结果合并器"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.merge_strategies: Dict[str, Callable] = {}
        self.lock = threading.Lock()
    
    def register_merge_strategy(self, result_type: str, merge_func: Callable):
        """注册合并策略"""
        self.merge_strategies[result_type] = merge_func
    
    def add_result(self, result_type: str, task_id: str, data: Any):
        """添加结果"""
        with self.lock:
            if result_type not in self.results:
                self.results[result_type] = {}
            
            self.results[result_type][task_id] = data
    
    def merge_results(self, result_type: str) -> Any:
        """合并指定类型的结果"""
        with self.lock:
            if result_type not in self.results:
                return None
            
            results_data = self.results[result_type]
            
            if result_type in self.merge_strategies:
                # 使用自定义合并策略
                return self.merge_strategies[result_type](results_data)
            else:
                # 默认合并策略：简单列表合并
                return self._default_merge(results_data)
    
    def _default_merge(self, results_data: Dict[str, Any]) -> List[Any]:
        """默认合并策略"""
        merged = []
        
        for task_id in sorted(results_data.keys()):
            data = results_data[task_id]
            
            if isinstance(data, list):
                merged.extend(data)
            else:
                merged.append(data)
        
        return merged
    
    def get_all_merged_results(self) -> Dict[str, Any]:
        """获取所有合并后的结果"""
        merged_results = {}
        
        for result_type in self.results.keys():
            merged_results[result_type] = self.merge_results(result_type)
        
        return merged_results