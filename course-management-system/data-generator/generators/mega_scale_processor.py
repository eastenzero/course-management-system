# file: data-generator/generators/mega_scale_processor.py
# 功能: 百万级数据分批处理机制

from typing import Dict, List, Any, Optional, Callable, Generator, Tuple
from dataclasses import dataclass, field
from enum import Enum
import gc
import psutil
import threading
import queue
import time
import json
import pickle
import gzip
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp

from constraint_aware_generator import ConstraintAwareCourseGenerator, GenerationConfig


class ProcessingMode(Enum):
    """处理模式"""
    SEQUENTIAL = "顺序处理"
    PARALLEL_THREAD = "线程并行"
    PARALLEL_PROCESS = "进程并行"
    HYBRID = "混合模式"


class MemoryStrategy(Enum):
    """内存策略"""
    CONSERVATIVE = "保守策略"  # 低内存使用
    BALANCED = "平衡策略"     # 中等内存使用
    AGGRESSIVE = "激进策略"   # 高内存使用


@dataclass
class BatchConfig:
    """分批配置"""
    batch_size: int = 2000
    max_memory_mb: int = 4096
    memory_threshold: float = 0.8
    gc_frequency: int = 5
    checkpoint_interval: int = 10000
    compression_enabled: bool = True
    
    # 并行配置
    max_workers: int = 4
    processing_mode: ProcessingMode = ProcessingMode.HYBRID
    
    # 内存管理
    memory_strategy: MemoryStrategy = MemoryStrategy.BALANCED
    enable_object_pool: bool = True
    enable_streaming: bool = True
    
    # 检查点配置
    checkpoint_dir: str = "checkpoints"
    auto_resume: bool = True
    cleanup_checkpoints: bool = True


@dataclass
class BatchMetrics:
    """批次指标"""
    batch_id: int
    records_processed: int
    processing_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    errors_count: int = 0
    quality_score: float = 1.0


class MemoryManager:
    """内存管理器"""
    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MemoryManager")
        self.object_pools: Dict[str, List[Any]] = {}
        self._memory_monitor = threading.Thread(target=self._monitor_memory, daemon=True)
        self._monitoring = False
        
    def start_monitoring(self):
        """开始内存监控"""
        self._monitoring = True
        self._memory_monitor.start()
        
    def stop_monitoring(self):
        """停止内存监控"""
        self._monitoring = False
        if self._memory_monitor.is_alive():
            self._memory_monitor.join()
            
    def _monitor_memory(self):
        """内存监控线程"""
        while self._monitoring:
            memory_percent = psutil.virtual_memory().percent / 100.0
            
            if memory_percent > self.config.memory_threshold:
                self.logger.warning(f"内存使用率 {memory_percent:.1%} 超过阈值 {self.config.memory_threshold:.1%}")
                self.force_gc()
                
            time.sleep(1)
            
    def get_object(self, object_type: str, factory: Callable[[], Any]) -> Any:
        """从对象池获取对象"""
        if not self.config.enable_object_pool:
            return factory()
            
        pool = self.object_pools.setdefault(object_type, [])
        
        if pool:
            return pool.pop()
        else:
            return factory()
            
    def return_object(self, object_type: str, obj: Any):
        """归还对象到对象池"""
        if not self.config.enable_object_pool:
            return
            
        pool = self.object_pools.setdefault(object_type, [])
        
        # 限制池大小
        if len(pool) < 100:
            # 清理对象状态
            if hasattr(obj, 'reset'):
                obj.reset()
            pool.append(obj)
            
    def force_gc(self):
        """强制垃圾回收"""
        self.logger.debug("执行强制垃圾回收")
        
        # 清空对象池
        for pool in self.object_pools.values():
            pool.clear()
            
        # 多次垃圾回收
        for _ in range(3):
            gc.collect()
            
    def get_memory_usage(self) -> float:
        """获取当前内存使用率"""
        return psutil.virtual_memory().percent / 100.0
        
    def get_available_memory_mb(self) -> float:
        """获取可用内存(MB)"""
        return psutil.virtual_memory().available / (1024 * 1024)


class CheckpointManager:
    """检查点管理器"""
    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.checkpoint_dir = Path(config.checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(f"{__name__}.CheckpointManager")
        
    def save_checkpoint(self, batch_id: int, data: Dict[str, Any], metadata: Dict[str, Any]):
        """保存检查点"""
        try:
            checkpoint_file = self.checkpoint_dir / f"checkpoint_{batch_id:06d}.pkl"
            
            checkpoint_data = {
                'batch_id': batch_id,
                'data': data,
                'metadata': metadata,
                'timestamp': time.time()
            }
            
            # 使用压缩保存
            if self.config.compression_enabled:
                with gzip.open(f"{checkpoint_file}.gz", 'wb') as f:
                    pickle.dump(checkpoint_data, f)
                checkpoint_file = f"{checkpoint_file}.gz"
            else:
                with open(checkpoint_file, 'wb') as f:
                    pickle.dump(checkpoint_data, f)
                    
            self.logger.debug(f"保存检查点: {checkpoint_file}")
            return str(checkpoint_file)
            
        except Exception as e:
            self.logger.error(f"保存检查点失败: {e}")
            return None
            
    def load_checkpoint(self, batch_id: int) -> Optional[Dict[str, Any]]:
        """加载检查点"""
        try:
            # 尝试压缩文件
            checkpoint_file = self.checkpoint_dir / f"checkpoint_{batch_id:06d}.pkl.gz"
            if checkpoint_file.exists():
                with gzip.open(checkpoint_file, 'rb') as f:
                    return pickle.load(f)
                    
            # 尝试未压缩文件
            checkpoint_file = self.checkpoint_dir / f"checkpoint_{batch_id:06d}.pkl"
            if checkpoint_file.exists():
                with open(checkpoint_file, 'rb') as f:
                    return pickle.load(f)
                    
            return None
            
        except Exception as e:
            self.logger.error(f"加载检查点失败: {e}")
            return None
            
    def find_latest_checkpoint(self) -> Optional[int]:
        """查找最新的检查点"""
        checkpoint_files = list(self.checkpoint_dir.glob("checkpoint_*.pkl*"))
        
        if not checkpoint_files:
            return None
            
        # 提取批次ID并排序
        batch_ids = []
        for file in checkpoint_files:
            try:
                # 从文件名提取批次ID
                batch_id = int(file.stem.split('_')[1].split('.')[0])
                batch_ids.append(batch_id)
            except (ValueError, IndexError):
                continue
                
        return max(batch_ids) if batch_ids else None
        
    def cleanup_old_checkpoints(self, keep_latest: int = 10):
        """清理旧检查点"""
        if not self.config.cleanup_checkpoints:
            return
            
        checkpoint_files = list(self.checkpoint_dir.glob("checkpoint_*.pkl*"))
        
        if len(checkpoint_files) <= keep_latest:
            return
            
        # 按修改时间排序，保留最新的
        checkpoint_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        for file in checkpoint_files[keep_latest:]:
            try:
                file.unlink()
                self.logger.debug(f"删除旧检查点: {file}")
            except Exception as e:
                self.logger.error(f"删除检查点失败: {e}")


class BatchProcessor:
    """批处理器"""
    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.memory_manager = MemoryManager(config)
        self.checkpoint_manager = CheckpointManager(config)
        self.logger = logging.getLogger(f"{__name__}.BatchProcessor")
        
        self.metrics: List[BatchMetrics] = []
        self.total_processed = 0
        self.start_time = 0
        
    def process_batches(self, generator_func: Callable, total_records: int, 
                       resume_from: Optional[int] = None) -> Generator[BatchMetrics, None, None]:
        """处理批次"""
        self.start_time = time.time()
        self.memory_manager.start_monitoring()
        
        try:
            # 确定起始批次
            start_batch = resume_from or 0
            if start_batch == 0 and self.config.auto_resume:
                latest_checkpoint = self.checkpoint_manager.find_latest_checkpoint()
                if latest_checkpoint is not None:
                    start_batch = latest_checkpoint + 1
                    self.logger.info(f"从检查点恢复，起始批次: {start_batch}")
                    
            # 计算总批次数
            total_batches = (total_records + self.config.batch_size - 1) // self.config.batch_size
            
            # 根据处理模式选择处理方法
            if self.config.processing_mode == ProcessingMode.SEQUENTIAL:
                yield from self._process_sequential(generator_func, start_batch, total_batches)
            elif self.config.processing_mode == ProcessingMode.PARALLEL_THREAD:
                yield from self._process_parallel_thread(generator_func, start_batch, total_batches)
            elif self.config.processing_mode == ProcessingMode.PARALLEL_PROCESS:
                yield from self._process_parallel_process(generator_func, start_batch, total_batches)
            else:  # HYBRID
                yield from self._process_hybrid(generator_func, start_batch, total_batches)
                
        finally:
            self.memory_manager.stop_monitoring()
            
    def _process_sequential(self, generator_func: Callable, start_batch: int, 
                          total_batches: int) -> Generator[BatchMetrics, None, None]:
        """顺序处理"""
        for batch_id in range(start_batch, total_batches):
            yield from self._process_single_batch(generator_func, batch_id)
            
    def _process_parallel_thread(self, generator_func: Callable, start_batch: int, 
                               total_batches: int) -> Generator[BatchMetrics, None, None]:
        """线程并行处理"""
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # 提交批次任务
            future_to_batch = {}
            
            # 限制并发数量以控制内存使用
            active_batches = 0
            max_active = self.config.max_workers * 2
            
            for batch_id in range(start_batch, total_batches):
                if active_batches >= max_active:
                    # 等待一些任务完成
                    for future in as_completed(list(future_to_batch.keys()), timeout=60):
                        batch_metrics = future.result()
                        del future_to_batch[future]
                        active_batches -= 1
                        yield batch_metrics
                        break
                        
                future = executor.submit(self._process_batch_wrapper, generator_func, batch_id)
                future_to_batch[future] = batch_id
                active_batches += 1
                
            # 处理剩余任务
            for future in as_completed(future_to_batch.keys()):
                batch_metrics = future.result()
                yield batch_metrics
                
    def _process_parallel_process(self, generator_func: Callable, start_batch: int, 
                                total_batches: int) -> Generator[BatchMetrics, None, None]:
        """进程并行处理"""
        with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            # 进程池处理
            batch_range = range(start_batch, total_batches)
            
            for batch_metrics in executor.map(
                self._process_batch_in_process, 
                [(generator_func, batch_id, self.config) for batch_id in batch_range]
            ):
                yield batch_metrics
                
    def _process_hybrid(self, generator_func: Callable, start_batch: int, 
                       total_batches: int) -> Generator[BatchMetrics, None, None]:
        """混合模式处理"""
        # 根据系统资源动态选择处理模式
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        if memory_gb > 16 and cpu_count >= 8:
            # 高配置：使用进程并行
            yield from self._process_parallel_process(generator_func, start_batch, total_batches)
        elif memory_gb > 8 and cpu_count >= 4:
            # 中等配置：使用线程并行
            yield from self._process_parallel_thread(generator_func, start_batch, total_batches)
        else:
            # 低配置：使用顺序处理
            yield from self._process_sequential(generator_func, start_batch, total_batches)
            
    def _process_single_batch(self, generator_func: Callable, batch_id: int) -> Generator[BatchMetrics, None, None]:
        """处理单个批次"""
        batch_start_time = time.time()
        
        try:
            # 记录处理前的系统状态
            memory_before = self.memory_manager.get_memory_usage()
            cpu_before = psutil.cpu_percent(interval=None)
            
            # 生成批次数据
            batch_data = generator_func(batch_id, self.config.batch_size)
            
            # 处理数据
            processed_data = self._apply_data_processing(batch_data)
            
            # 保存检查点
            if batch_id % (self.config.checkpoint_interval // self.config.batch_size) == 0:
                self.checkpoint_manager.save_checkpoint(
                    batch_id, 
                    processed_data, 
                    {'total_processed': self.total_processed}
                )
                
            # 记录处理后的系统状态
            memory_after = self.memory_manager.get_memory_usage()
            cpu_after = psutil.cpu_percent(interval=None)
            
            processing_time = time.time() - batch_start_time
            
            # 创建批次指标
            metrics = BatchMetrics(
                batch_id=batch_id,
                records_processed=len(processed_data) if isinstance(processed_data, (list, dict)) else self.config.batch_size,
                processing_time=processing_time,
                memory_usage_mb=psutil.virtual_memory().used / (1024 * 1024),
                cpu_usage_percent=max(cpu_before, cpu_after)
            )
            
            self.metrics.append(metrics)
            self.total_processed += metrics.records_processed
            
            # 内存管理
            if batch_id % self.config.gc_frequency == 0:
                self.memory_manager.force_gc()
                
            yield metrics
            
        except Exception as e:
            self.logger.error(f"批次 {batch_id} 处理失败: {e}")
            
            error_metrics = BatchMetrics(
                batch_id=batch_id,
                records_processed=0,
                processing_time=time.time() - batch_start_time,
                memory_usage_mb=psutil.virtual_memory().used / (1024 * 1024),
                cpu_usage_percent=psutil.cpu_percent(interval=None),
                errors_count=1,
                quality_score=0.0
            )
            
            yield error_metrics
            
    def _process_batch_wrapper(self, generator_func: Callable, batch_id: int) -> BatchMetrics:
        """批次处理包装器（用于线程池）"""
        return next(self._process_single_batch(generator_func, batch_id))
        
    def _apply_data_processing(self, batch_data: Any) -> Any:
        """应用数据处理逻辑"""
        # 这里可以添加具体的数据处理逻辑
        # 例如：数据验证、格式转换、质量检查等
        return batch_data
        
    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        if not self.metrics:
            return {}
            
        total_time = time.time() - self.start_time
        total_errors = sum(m.errors_count for m in self.metrics)
        avg_processing_time = sum(m.processing_time for m in self.metrics) / len(self.metrics)
        avg_memory_usage = sum(m.memory_usage_mb for m in self.metrics) / len(self.metrics)
        avg_cpu_usage = sum(m.cpu_usage_percent for m in self.metrics) / len(self.metrics)
        avg_quality_score = sum(m.quality_score for m in self.metrics) / len(self.metrics)
        
        processing_speed = self.total_processed / max(1, total_time)
        
        return {
            'total_processed': self.total_processed,
            'total_batches': len(self.metrics),
            'total_time_seconds': total_time,
            'total_errors': total_errors,
            'processing_speed_records_per_second': processing_speed,
            'average_batch_processing_time': avg_processing_time,
            'average_memory_usage_mb': avg_memory_usage,
            'average_cpu_usage_percent': avg_cpu_usage,
            'average_quality_score': avg_quality_score,
            'error_rate': total_errors / max(1, self.total_processed)
        }


@staticmethod
def _process_batch_in_process(args: Tuple[Callable, int, BatchConfig]) -> BatchMetrics:
    """在独立进程中处理批次"""
    generator_func, batch_id, config = args
    
    # 在子进程中重新创建处理器
    processor = BatchProcessor(config)
    return next(processor._process_single_batch(generator_func, batch_id))


class MegaScaleDataGenerator:
    """百万级数据生成器"""
    
    def __init__(self, generation_config: GenerationConfig, batch_config: BatchConfig):
        self.generation_config = generation_config
        self.batch_config = batch_config
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.batch_processor = BatchProcessor(batch_config)
        self.base_generator = ConstraintAwareCourseGenerator(generation_config)
        
    def generate_mega_dataset(self, output_dir: str = "mega_output") -> Dict[str, Any]:
        """生成百万级数据集"""
        self.logger.info(f"开始生成百万级数据集，目标规模: {self.generation_config.target_students:,} 学生")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 定义数据生成函数
        def data_generator(batch_id: int, batch_size: int) -> Dict[str, Any]:
            # 为每个批次调整配置
            batch_config = self._create_batch_generation_config(batch_id, batch_size)
            
            # 创建批次生成器
            batch_generator = ConstraintAwareCourseGenerator(batch_config)
            
            # 生成批次数据
            return batch_generator.generate_complete_dataset()
            
        # 计算总记录数（以学生为基准）
        total_records = self.generation_config.target_students
        
        # 处理批次
        all_metrics = []
        all_data = {
            'teachers': [],
            'courses': [],
            'schedules': [],
            'prerequisites': [],
            'students': []
        }
        
        try:
            for metrics in self.batch_processor.process_batches(data_generator, total_records):
                all_metrics.append(metrics)
                
                # 实时进度报告
                progress = (metrics.batch_id + 1) * self.batch_config.batch_size
                self.logger.info(
                    f"批次 {metrics.batch_id:>6d} 完成 | "
                    f"处理 {metrics.records_processed:>8,} 记录 | "
                    f"用时 {metrics.processing_time:>6.2f}s | "
                    f"内存 {metrics.memory_usage_mb:>8.1f}MB | "
                    f"进度 {min(100, progress / total_records * 100):>6.1f}%"
                )
                
                # 定期保存中间结果
                if metrics.batch_id % 10 == 0:
                    self._save_intermediate_results(all_data, output_path, metrics.batch_id)
                    
        except KeyboardInterrupt:
            self.logger.warning("用户中断，保存已处理的数据...")
            
        except Exception as e:
            self.logger.error(f"处理过程中发生错误: {e}")
            raise
            
        finally:
            # 保存最终结果
            self._save_final_results(all_data, output_path)
            
            # 生成处理报告
            stats = self.batch_processor.get_processing_statistics()
            self._save_processing_report(stats, all_metrics, output_path)
            
        return {
            'output_directory': str(output_path),
            'processing_statistics': stats,
            'data_summary': self._create_data_summary(all_data)
        }
        
    def _create_batch_generation_config(self, batch_id: int, batch_size: int) -> GenerationConfig:
        """为批次创建生成配置"""
        # 根据批次调整规模
        scale_factor = batch_size / self.generation_config.target_students
        
        return GenerationConfig(
            target_students=batch_size,
            target_teachers=max(10, int(self.generation_config.target_teachers * scale_factor)),
            target_courses=max(50, int(self.generation_config.target_courses * scale_factor)),
            target_schedules=max(100, int(self.generation_config.target_schedules * scale_factor)),
            
            # 继承其他配置
            enable_prerequisite_constraints=self.generation_config.enable_prerequisite_constraints,
            enable_time_conflict_detection=self.generation_config.enable_time_conflict_detection,
            enable_capacity_constraints=self.generation_config.enable_capacity_constraints,
            enable_teacher_workload_limits=self.generation_config.enable_teacher_workload_limits,
            
            realism_level=self.generation_config.realism_level,
            constraint_strictness=self.generation_config.constraint_strictness,
            semester_count=self.generation_config.semester_count,
            departments=self.generation_config.departments
        )
        
    def _save_intermediate_results(self, data: Dict[str, Any], output_path: Path, batch_id: int):
        """保存中间结果"""
        try:
            intermediate_file = output_path / f"intermediate_{batch_id:06d}.json"
            
            with open(intermediate_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'batch_id': batch_id,
                    'timestamp': time.time(),
                    'data_counts': {k: len(v) for k, v in data.items()}
                }, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"保存中间结果失败: {e}")
            
    def _save_final_results(self, data: Dict[str, Any], output_path: Path):
        """保存最终结果"""
        try:
            final_file = output_path / "final_dataset.json"
            
            with open(final_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"最终数据集已保存到: {final_file}")
            
        except Exception as e:
            self.logger.error(f"保存最终结果失败: {e}")
            
    def _save_processing_report(self, stats: Dict[str, Any], metrics: List[BatchMetrics], 
                              output_path: Path):
        """保存处理报告"""
        try:
            report_file = output_path / "processing_report.json"
            
            report = {
                'generation_config': self.generation_config.__dict__,
                'batch_config': self.batch_config.__dict__,
                'processing_statistics': stats,
                'batch_metrics': [m.__dict__ for m in metrics],
                'timestamp': time.time()
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                
            self.logger.info(f"处理报告已保存到: {report_file}")
            
        except Exception as e:
            self.logger.error(f"保存处理报告失败: {e}")
            
    def _create_data_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建数据摘要"""
        return {
            'total_teachers': len(data.get('teachers', [])),
            'total_courses': len(data.get('courses', [])),
            'total_schedules': len(data.get('schedules', [])),
            'total_prerequisites': len(data.get('prerequisites', [])),
            'total_students': len(data.get('students', [])),
            'generation_timestamp': time.time()
        }