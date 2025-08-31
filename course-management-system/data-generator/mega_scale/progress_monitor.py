# file: data-generator/mega_scale/progress_monitor.py
# 功能: 进度监控和错误处理机制

import time
import threading
import json
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from queue import Queue, Empty
from collections import deque
import psutil
from tqdm import tqdm


@dataclass
class ProgressMetrics:
    """进度指标"""
    total_records: int = 0
    processed_records: int = 0
    failed_records: int = 0
    start_time: float = 0.0
    current_time: float = 0.0
    estimated_finish_time: Optional[float] = None
    processing_speed: float = 0.0  # 记录/秒
    
    @property
    def progress_percent(self) -> float:
        if self.total_records == 0:
            return 0.0
        return (self.processed_records / self.total_records) * 100
    
    @property
    def elapsed_time(self) -> float:
        return self.current_time - self.start_time
    
    @property
    def remaining_time(self) -> Optional[float]:
        if self.estimated_finish_time:
            return max(0, self.estimated_finish_time - self.current_time)
        return None


@dataclass
class SystemMetrics:
    """系统性能指标"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0
    network_io_sent_mb: float = 0.0
    network_io_recv_mb: float = 0.0
    gc_count: int = 0
    active_threads: int = 0


@dataclass
class ErrorInfo:
    """错误信息"""
    error_id: str
    timestamp: float
    error_type: str
    error_message: str
    stack_trace: str
    context: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"  # low, medium, high, critical
    resolved: bool = False


@dataclass
class Checkpoint:
    """检查点信息"""
    checkpoint_id: str
    timestamp: float
    processed_records: int
    data_summary: Dict[str, Any]
    system_state: Dict[str, Any]


class ProgressCalculator:
    """进度计算器"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.speed_history = deque(maxlen=window_size)
        self.time_history = deque(maxlen=window_size)
        self.last_update_time = time.time()
        self.last_processed_count = 0
    
    def update(self, processed_records: int) -> float:
        """更新并计算处理速度"""
        current_time = time.time()
        
        if self.last_update_time > 0:
            time_diff = current_time - self.last_update_time
            record_diff = processed_records - self.last_processed_count
            
            if time_diff > 0:
                speed = record_diff / time_diff
                self.speed_history.append(speed)
                self.time_history.append(current_time)
        
        self.last_update_time = current_time
        self.last_processed_count = processed_records
        
        # 计算平均速度
        if self.speed_history:
            return sum(self.speed_history) / len(self.speed_history)
        return 0.0
    
    def estimate_finish_time(self, total_records: int, processed_records: int) -> Optional[float]:
        """估算完成时间"""
        if not self.speed_history or processed_records == 0:
            return None
        
        avg_speed = sum(self.speed_history) / len(self.speed_history)
        if avg_speed <= 0:
            return None
        
        remaining_records = total_records - processed_records
        remaining_time = remaining_records / avg_speed
        
        return time.time() + remaining_time


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, max_errors: int = 1000):
        self.max_errors = max_errors
        self.errors: Dict[str, ErrorInfo] = {}
        self.error_counts: Dict[str, int] = {}
        self.error_patterns: Dict[str, Callable] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.lock = threading.Lock()
        
        # 错误统计
        self.total_errors = 0
        self.critical_errors = 0
        self.resolved_errors = 0
    
    def register_error_pattern(self, pattern_name: str, detector: Callable[[Exception], bool]):
        """注册错误模式检测器"""
        self.error_patterns[pattern_name] = detector
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """注册恢复策略"""
        self.recovery_strategies[error_type] = strategy
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
        """处理错误"""
        with self.lock:
            error_id = f"error_{int(time.time() * 1000000)}"
            error_type = type(error).__name__
            
            # 检测错误模式
            detected_patterns = []
            for pattern_name, detector in self.error_patterns.items():
                try:
                    if detector(error):
                        detected_patterns.append(pattern_name)
                except:
                    pass
            
            # 确定严重性
            severity = self._determine_severity(error, detected_patterns)
            
            # 创建错误信息
            error_info = ErrorInfo(
                error_id=error_id,
                timestamp=time.time(),
                error_type=error_type,
                error_message=str(error),
                stack_trace=traceback.format_exc(),
                context=context or {},
                severity=severity
            )
            
            # 存储错误
            self.errors[error_id] = error_info
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
            self.total_errors += 1
            
            if severity == "critical":
                self.critical_errors += 1
            
            # 尝试恢复
            if error_type in self.recovery_strategies:
                try:
                    recovery_result = self.recovery_strategies[error_type](error, context)
                    if recovery_result:
                        error_info.resolved = True
                        self.resolved_errors += 1
                except Exception as recovery_error:
                    print(f"恢复策略执行失败: {recovery_error}")
            
            # 清理旧错误
            self._cleanup_old_errors()
            
            return error_info
    
    def _determine_severity(self, error: Exception, patterns: List[str]) -> str:
        """确定错误严重性"""
        if isinstance(error, (MemoryError, SystemExit, KeyboardInterrupt)):
            return "critical"
        elif isinstance(error, (FileNotFoundError, PermissionError)):
            return "high"
        elif isinstance(error, (ValueError, TypeError)):
            return "medium"
        else:
            return "low"
    
    def _cleanup_old_errors(self):
        """清理旧错误"""
        if len(self.errors) <= self.max_errors:
            return
        
        # 按时间排序，保留最新的错误
        sorted_errors = sorted(self.errors.items(), key=lambda x: x[1].timestamp)
        
        # 删除最旧的错误
        to_delete = len(self.errors) - self.max_errors
        for i in range(to_delete):
            error_id = sorted_errors[i][0]
            del self.errors[error_id]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        with self.lock:
            recent_errors = [
                error for error in self.errors.values()
                if time.time() - error.timestamp < 3600  # 最近1小时
            ]
            
            return {
                'total_errors': self.total_errors,
                'critical_errors': self.critical_errors,
                'resolved_errors': self.resolved_errors,
                'recent_errors': len(recent_errors),
                'error_types': dict(self.error_counts),
                'error_rate': len(recent_errors) / 3600,  # 每秒错误数
                'resolution_rate': (self.resolved_errors / max(self.total_errors, 1)) * 100
            }


class CheckpointManager:
    """检查点管理器"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints", interval: int = 100000):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.interval = interval
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.last_checkpoint_time = 0.0
        self.lock = threading.Lock()
    
    def should_create_checkpoint(self, processed_records: int) -> bool:
        """是否应该创建检查点"""
        time_since_last = time.time() - self.last_checkpoint_time
        
        return (
            processed_records % self.interval == 0 or
            time_since_last > 300  # 超过5分钟
        )
    
    def create_checkpoint(self, processed_records: int, 
                         data_summary: Dict[str, Any],
                         system_state: Dict[str, Any]) -> str:
        """创建检查点"""
        with self.lock:
            checkpoint_id = f"checkpoint_{int(time.time())}"
            timestamp = time.time()
            
            checkpoint = Checkpoint(
                checkpoint_id=checkpoint_id,
                timestamp=timestamp,
                processed_records=processed_records,
                data_summary=data_summary,
                system_state=system_state
            )
            
            self.checkpoints[checkpoint_id] = checkpoint
            
            # 保存到文件
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
            
            checkpoint_data = {
                'checkpoint_id': checkpoint_id,
                'timestamp': timestamp,
                'processed_records': processed_records,
                'data_summary': data_summary,
                'system_state': system_state
            }
            
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            
            self.last_checkpoint_time = timestamp
            
            # 清理旧检查点
            self._cleanup_old_checkpoints()
            
            return checkpoint_id
    
    def _cleanup_old_checkpoints(self):
        """清理旧检查点"""
        # 保留最近10个检查点
        sorted_checkpoints = sorted(
            self.checkpoints.items(),
            key=lambda x: x[1].timestamp,
            reverse=True
        )
        
        if len(sorted_checkpoints) > 10:
            for checkpoint_id, checkpoint in sorted_checkpoints[10:]:
                # 删除文件
                checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
                if checkpoint_file.exists():
                    checkpoint_file.unlink()
                
                # 删除内存中的记录
                if checkpoint_id in self.checkpoints:
                    del self.checkpoints[checkpoint_id]
    
    def get_latest_checkpoint(self) -> Optional[Checkpoint]:
        """获取最新检查点"""
        with self.lock:
            if not self.checkpoints:
                return None
            
            latest = max(self.checkpoints.values(), key=lambda x: x.timestamp)
            return latest


class ProgressMonitor:
    """进度监控器"""
    
    def __init__(self, total_records: int = 0):
        self.total_records = total_records
        self.progress_calc = ProgressCalculator()
        self.error_handler = ErrorHandler()
        self.checkpoint_manager = CheckpointManager()
        
        # 当前状态
        self.current_metrics = ProgressMetrics(total_records=total_records)
        self.system_metrics = SystemMetrics()
        
        # 监控控制
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.update_interval = 1.0  # 更新间隔(秒)
        
        # 回调函数
        self.progress_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # 进度条
        self.progress_bar: Optional[tqdm] = None
        self.lock = threading.Lock()
    
    def start_monitoring(self, enable_progress_bar: bool = True):
        """开始监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.current_metrics.start_time = time.time()
        
        # 创建进度条
        if enable_progress_bar:
            self.progress_bar = tqdm(
                total=self.total_records,
                desc="数据生成进度",
                unit="条",
                unit_scale=True,
                bar_format='{desc}: {percentage:3.0f}%|{bar}| {n:,}/{total:,} [{elapsed}<{remaining}, {rate_fmt}]'
            )
        
        # 注册常见错误处理
        self._register_common_error_handlers()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        print("📊 进度监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None
        
        print("📊 进度监控已停止")
    
    def update_progress(self, processed_records: int, failed_records: int = 0):
        """更新进度"""
        with self.lock:
            self.current_metrics.processed_records = processed_records
            self.current_metrics.failed_records = failed_records
            self.current_metrics.current_time = time.time()
            
            # 计算处理速度
            self.current_metrics.processing_speed = self.progress_calc.update(processed_records)
            
            # 估算完成时间
            self.current_metrics.estimated_finish_time = self.progress_calc.estimate_finish_time(
                self.total_records, processed_records
            )
            
            # 更新进度条
            if self.progress_bar:
                delta = processed_records - self.progress_bar.n
                if delta > 0:
                    self.progress_bar.update(delta)
            
            # 检查是否需要创建检查点
            if self.checkpoint_manager.should_create_checkpoint(processed_records):
                self._create_checkpoint()
            
            # 调用进度回调
            for callback in self.progress_callbacks:
                try:
                    callback(self.current_metrics)
                except:
                    pass
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """处理错误"""
        error_info = self.error_handler.handle_error(error, context)
        
        # 调用错误回调
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except:
                pass
        
        return error_info.error_id
    
    def add_progress_callback(self, callback: Callable):
        """添加进度回调"""
        self.progress_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable):
        """添加错误回调"""
        self.error_callbacks.append(callback)
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 更新系统指标
                self._update_system_metrics()
                
                # 检查内存使用
                if self.system_metrics.memory_percent > 90:
                    print(f"⚠️ 内存使用率过高: {self.system_metrics.memory_percent:.1f}%")
                
                # 检查磁盘空间
                disk_usage = psutil.disk_usage('.')
                if disk_usage.percent > 90:
                    print(f"⚠️ 磁盘空间不足: {disk_usage.percent:.1f}%")
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"监控循环异常: {e}")
                time.sleep(5)
    
    def _update_system_metrics(self):
        """更新系统指标"""
        try:
            # CPU和内存
            self.system_metrics.cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            self.system_metrics.memory_percent = memory.percent
            self.system_metrics.memory_used_mb = memory.used / 1024 / 1024
            
            # 磁盘I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.system_metrics.disk_io_read_mb = disk_io.read_bytes / 1024 / 1024
                self.system_metrics.disk_io_write_mb = disk_io.write_bytes / 1024 / 1024
            
            # 网络I/O
            net_io = psutil.net_io_counters()
            if net_io:
                self.system_metrics.network_io_sent_mb = net_io.bytes_sent / 1024 / 1024
                self.system_metrics.network_io_recv_mb = net_io.bytes_recv / 1024 / 1024
            
            # 线程数
            self.system_metrics.active_threads = threading.active_count()
            
        except Exception as e:
            print(f"更新系统指标失败: {e}")
    
    def _create_checkpoint(self):
        """创建检查点"""
        try:
            data_summary = {
                'total_records': self.total_records,
                'processed_records': self.current_metrics.processed_records,
                'failed_records': self.current_metrics.failed_records,
                'progress_percent': self.current_metrics.progress_percent
            }
            
            system_state = {
                'memory_usage_mb': self.system_metrics.memory_used_mb,
                'cpu_percent': self.system_metrics.cpu_percent,
                'active_threads': self.system_metrics.active_threads,
                'processing_speed': self.current_metrics.processing_speed
            }
            
            checkpoint_id = self.checkpoint_manager.create_checkpoint(
                self.current_metrics.processed_records,
                data_summary,
                system_state
            )
            
            print(f"💾 创建检查点: {checkpoint_id}")
            
        except Exception as e:
            print(f"创建检查点失败: {e}")
    
    def _register_common_error_handlers(self):
        """注册常见错误处理器"""
        
        # 内存错误恢复策略
        def handle_memory_error(error: Exception, context: Dict[str, Any]):
            import gc
            gc.collect()
            print("🧹 内存不足，执行垃圾回收")
            return True
        
        # 文件权限错误恢复策略
        def handle_permission_error(error: Exception, context: Dict[str, Any]):
            print(f"🔒 文件权限错误: {error}")
            # 可以尝试更改权限或使用备用路径
            return False
        
        self.error_handler.register_recovery_strategy("MemoryError", handle_memory_error)
        self.error_handler.register_recovery_strategy("PermissionError", handle_permission_error)
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取状态报告"""
        with self.lock:
            return {
                'progress': {
                    'total_records': self.current_metrics.total_records,
                    'processed_records': self.current_metrics.processed_records,
                    'failed_records': self.current_metrics.failed_records,
                    'progress_percent': self.current_metrics.progress_percent,
                    'processing_speed': self.current_metrics.processing_speed,
                    'elapsed_time': self.current_metrics.elapsed_time,
                    'remaining_time': self.current_metrics.remaining_time
                },
                'system': {
                    'cpu_percent': self.system_metrics.cpu_percent,
                    'memory_percent': self.system_metrics.memory_percent,
                    'memory_used_mb': self.system_metrics.memory_used_mb,
                    'active_threads': self.system_metrics.active_threads,
                    'disk_io_read_mb': self.system_metrics.disk_io_read_mb,
                    'disk_io_write_mb': self.system_metrics.disk_io_write_mb
                },
                'errors': self.error_handler.get_error_summary(),
                'checkpoints': {
                    'total_checkpoints': len(self.checkpoint_manager.checkpoints),
                    'latest_checkpoint': self.checkpoint_manager.get_latest_checkpoint()
                }
            }
    
    def print_status(self):
        """打印状态信息"""
        report = self.get_status_report()
        
        print(f"\n📊 进度状态报告")
        print(f"{'='*60}")
        
        progress = report['progress']
        print(f"📈 进度: {progress['processed_records']:,}/{progress['total_records']:,} "
              f"({progress['progress_percent']:.1f}%)")
        print(f"⚡ 速度: {progress['processing_speed']:.0f} 条/秒")
        
        if progress['remaining_time']:
            remaining = timedelta(seconds=int(progress['remaining_time']))
            print(f"⏰ 预计剩余: {remaining}")
        
        system = report['system']
        print(f"💾 内存: {system['memory_used_mb']:.0f}MB ({system['memory_percent']:.1f}%)")
        print(f"🖥️ CPU: {system['cpu_percent']:.1f}%")
        
        errors = report['errors']
        if errors['total_errors'] > 0:
            print(f"❌ 错误: {errors['total_errors']} (解决率: {errors['resolution_rate']:.1f}%)")
        
        print(f"{'='*60}")