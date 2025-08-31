# file: data-generator/mega_scale/batch_manager.py
# 功能: 百万级数据生成的批处理管理器

import gc
import psutil
import time
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from pathlib import Path
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import json


@dataclass
class BatchConfig:
    """批处理配置"""
    batch_size: int = 50000           # 每批数据量
    max_memory_mb: int = 2048         # 最大内存限制(MB)
    max_workers: int = 4              # 最大工作进程数
    checkpoint_interval: int = 100000  # 检查点间隔
    gc_threshold: float = 0.8         # GC触发阈值
    enable_compression: bool = True    # 启用压缩
    enable_streaming: bool = True      # 启用流式处理


@dataclass
class BatchStatus:
    """批次状态"""
    batch_id: int
    total_records: int
    processed_records: int
    start_time: float
    estimated_finish_time: Optional[float] = None
    memory_usage_mb: float = 0.0
    error_count: int = 0
    status: str = "pending"  # pending, running, completed, failed


class DependencyGraph:
    """依赖关系图管理器"""
    
    def __init__(self):
        self.dependencies = {}
        self.reverse_dependencies = {}
    
    def add_dependency(self, dependent: str, dependency: str):
        """添加依赖关系: dependent依赖于dependency"""
        if dependent not in self.dependencies:
            self.dependencies[dependent] = set()
        self.dependencies[dependent].add(dependency)
        
        if dependency not in self.reverse_dependencies:
            self.reverse_dependencies[dependency] = set()
        self.reverse_dependencies[dependency].add(dependent)
    
    def get_execution_order(self, tasks: List[str]) -> List[str]:
        """获取任务执行顺序（拓扑排序）"""
        in_degree = {task: 0 for task in tasks}
        
        # 计算入度
        for task in tasks:
            for dep in self.dependencies.get(task, []):
                if dep in in_degree:
                    in_degree[task] += 1
        
        # 拓扑排序
        result = []
        queue = [task for task, degree in in_degree.items() if degree == 0]
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # 更新依赖该任务的其他任务
            for dependent in self.reverse_dependencies.get(current, []):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        # 检查是否有循环依赖
        if len(result) != len(tasks):
            remaining = [task for task in tasks if task not in result]
            raise ValueError(f"检测到循环依赖: {remaining}")
        
        return result


class MemoryMonitor:
    """内存监控器"""
    
    def __init__(self, max_memory_mb: int, gc_threshold: float = 0.8):
        self.max_memory_mb = max_memory_mb
        self.gc_threshold = gc_threshold
        self.process = psutil.Process()
    
    def get_memory_usage_mb(self) -> float:
        """获取当前内存使用量(MB)"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_memory_percent(self) -> float:
        """获取内存使用百分比"""
        return self.get_memory_usage_mb() / self.max_memory_mb
    
    def should_trigger_gc(self) -> bool:
        """是否应该触发垃圾回收"""
        return self.get_memory_percent() > self.gc_threshold
    
    def force_gc(self) -> float:
        """强制垃圾回收并返回回收的内存量(MB)"""
        before = self.get_memory_usage_mb()
        gc.collect()
        after = self.get_memory_usage_mb()
        return before - after


class BatchProcessingManager:
    """批处理管理器"""
    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.dependency_graph = DependencyGraph()
        self.memory_monitor = MemoryMonitor(config.max_memory_mb, config.gc_threshold)
        self.batch_statuses: Dict[int, BatchStatus] = {}
        self.checkpoint_data = {}
        self.lock = threading.Lock()
        
        # 性能统计
        self.total_processed = 0
        self.start_time = None
        self.errors = []
    
    def calculate_optimal_batch_size(self, total_records: int, 
                                   estimated_record_size_bytes: int = 1024) -> int:
        """计算最优批次大小"""
        # 基于内存限制计算
        max_memory_bytes = self.config.max_memory_mb * 1024 * 1024
        memory_based_batch_size = int(max_memory_bytes * 0.5 / estimated_record_size_bytes)
        
        # 基于处理器核心数调整
        cpu_count = psutil.cpu_count()
        cpu_based_batch_size = self.config.batch_size * cpu_count
        
        # 基于总记录数调整
        if total_records < 100000:
            size_based_batch_size = min(10000, total_records // 10)
        else:
            size_based_batch_size = min(self.config.batch_size, total_records // 20)
        
        # 取最小值作为最优大小
        optimal_size = min(
            memory_based_batch_size,
            cpu_based_batch_size,
            size_based_batch_size,
            self.config.batch_size
        )
        
        return max(1000, optimal_size)  # 最小1000条记录
    
    def create_batches(self, total_records: int, 
                      task_dependencies: Dict[str, List[str]] = None) -> List[Dict[str, Any]]:
        """创建批次计划"""
        batch_size = self.calculate_optimal_batch_size(total_records)
        total_batches = (total_records + batch_size - 1) // batch_size
        
        batches = []
        for i in range(total_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_records)
            
            batch = {
                'batch_id': i,
                'start_idx': start_idx,
                'end_idx': end_idx,
                'size': end_idx - start_idx,
                'dependencies': [],
                'status': 'pending'
            }
            batches.append(batch)
        
        # 设置任务依赖关系
        if task_dependencies:
            for task, deps in task_dependencies.items():
                for dep in deps:
                    self.dependency_graph.add_dependency(task, dep)
        
        return batches
    
    def process_batch(self, batch_info: Dict[str, Any], 
                     processing_func: Callable, 
                     *args, **kwargs) -> Dict[str, Any]:
        """处理单个批次"""
        batch_id = batch_info['batch_id']
        
        # 创建批次状态
        status = BatchStatus(
            batch_id=batch_id,
            total_records=batch_info['size'],
            processed_records=0,
            start_time=time.time(),
            status="running"
        )
        
        with self.lock:
            self.batch_statuses[batch_id] = status
        
        try:
            # 内存检查
            if self.memory_monitor.should_trigger_gc():
                freed_mb = self.memory_monitor.force_gc()
                print(f"🧹 批次 {batch_id}: 执行垃圾回收，释放 {freed_mb:.1f}MB")
            
            # 执行处理函数
            result = processing_func(
                batch_info['start_idx'], 
                batch_info['end_idx'],
                *args, **kwargs
            )
            
            # 更新状态
            with self.lock:
                status.processed_records = batch_info['size']
                status.memory_usage_mb = self.memory_monitor.get_memory_usage_mb()
                status.status = "completed"
                self.total_processed += batch_info['size']
            
            # 检查点保存
            if self.total_processed % self.config.checkpoint_interval == 0:
                self._save_checkpoint(batch_id, result)
            
            return {
                'batch_id': batch_id,
                'success': True,
                'result': result,
                'processing_time': time.time() - status.start_time,
                'memory_usage_mb': status.memory_usage_mb
            }
            
        except Exception as e:
            with self.lock:
                status.status = "failed"
                status.error_count += 1
                self.errors.append({
                    'batch_id': batch_id,
                    'error': str(e),
                    'timestamp': time.time()
                })
            
            return {
                'batch_id': batch_id,
                'success': False,
                'error': str(e),
                'processing_time': time.time() - status.start_time
            }
    
    def process_batches_parallel(self, batches: List[Dict[str, Any]], 
                               processing_func: Callable,
                               *args, **kwargs) -> List[Dict[str, Any]]:
        """并行处理批次"""
        self.start_time = time.time()
        results = []
        
        # 根据依赖关系确定执行顺序
        batch_names = [f"batch_{b['batch_id']}" for b in batches]
        execution_order = self.dependency_graph.get_execution_order(batch_names)
        
        # 按依赖顺序创建批次映射
        batch_map = {f"batch_{b['batch_id']}": b for b in batches}
        ordered_batches = [batch_map[name] for name in execution_order]
        
        # 使用线程池处理批次
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # 提交所有批次任务
            future_to_batch = {
                executor.submit(
                    self.process_batch, batch, processing_func, *args, **kwargs
                ): batch for batch in ordered_batches
            }
            
            # 收集结果
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # 打印进度
                    success_count = sum(1 for r in results if r['success'])
                    total_batches = len(batches)
                    progress = len(results) / total_batches * 100
                    
                    print(f"📦 批次 {result['batch_id']:3d}/{total_batches} "
                          f"{'✅' if result['success'] else '❌'} "
                          f"进度: {progress:5.1f}% "
                          f"内存: {result.get('memory_usage_mb', 0):.0f}MB")
                    
                except Exception as e:
                    print(f"❌ 批次处理异常: {e}")
                    results.append({
                        'batch_id': batch['batch_id'],
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    def _save_checkpoint(self, batch_id: int, data: Any):
        """保存检查点"""
        checkpoint_dir = Path("checkpoints")
        checkpoint_dir.mkdir(exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"checkpoint_batch_{batch_id}.json"
        
        checkpoint_data = {
            'batch_id': batch_id,
            'timestamp': time.time(),
            'total_processed': self.total_processed,
            'memory_usage_mb': self.memory_monitor.get_memory_usage_mb(),
            'data_summary': {
                'type': type(data).__name__,
                'size': len(data) if hasattr(data, '__len__') else 'unknown'
            }
        }
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """获取进度摘要"""
        with self.lock:
            total_batches = len(self.batch_statuses)
            completed = sum(1 for s in self.batch_statuses.values() if s.status == "completed")
            failed = sum(1 for s in self.batch_statuses.values() if s.status == "failed")
            running = sum(1 for s in self.batch_statuses.values() if s.status == "running")
            
            elapsed_time = time.time() - (self.start_time or time.time())
            
            # 计算预估完成时间
            if completed > 0 and elapsed_time > 0:
                avg_time_per_batch = elapsed_time / completed
                remaining_batches = total_batches - completed
                estimated_remaining_time = avg_time_per_batch * remaining_batches
            else:
                estimated_remaining_time = None
            
            return {
                'total_batches': total_batches,
                'completed': completed,
                'failed': failed,
                'running': running,
                'pending': total_batches - completed - failed - running,
                'total_processed': self.total_processed,
                'progress_percent': completed / total_batches * 100 if total_batches > 0 else 0,
                'elapsed_time_seconds': elapsed_time,
                'estimated_remaining_seconds': estimated_remaining_time,
                'current_memory_mb': self.memory_monitor.get_memory_usage_mb(),
                'memory_usage_percent': self.memory_monitor.get_memory_percent() * 100,
                'error_count': len(self.errors),
                'processing_speed_records_per_second': self.total_processed / elapsed_time if elapsed_time > 0 else 0
            }
    
    def cleanup(self):
        """清理资源"""
        # 强制垃圾回收
        self.memory_monitor.force_gc()
        
        # 清理检查点文件
        checkpoint_dir = Path("checkpoints")
        if checkpoint_dir.exists():
            for file in checkpoint_dir.glob("checkpoint_batch_*.json"):
                try:
                    file.unlink()
                except:
                    pass