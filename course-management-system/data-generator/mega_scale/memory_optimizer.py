# file: data-generator/mega_scale/memory_optimizer.py
# 功能: 内存优化模块和流式写入机制

import gc
import gzip
import json
import threading
import weakref
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Iterator, TextIO
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
import psutil
import time
from dataclasses import dataclass, field


@dataclass
class MemoryPool:
    """内存池配置"""
    max_objects: int = 10000          # 最大对象数
    cleanup_threshold: float = 0.8    # 清理阈值
    object_lifetime: float = 300.0    # 对象生存时间(秒)


@dataclass
class StreamConfig:
    """流式处理配置"""
    buffer_size: int = 64 * 1024      # 写入缓冲区大小 (64KB)
    compression_level: int = 6         # 压缩级别 (1-9)
    max_file_size_mb: int = 500       # 单文件最大大小 (MB)
    enable_async_write: bool = True    # 异步写入
    write_queue_size: int = 1000      # 写入队列大小


class ObjectPool:
    """对象池管理器"""
    
    def __init__(self, config: MemoryPool):
        self.config = config
        self.pools: Dict[str, List[Any]] = {}
        self.object_timestamps: Dict[id, float] = {}
        self.lock = threading.Lock()
        self.weak_refs: Dict[str, List[weakref.ref]] = {}
        
        # 启动清理线程
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
    
    def get_object(self, object_type: str, factory_func: callable) -> Any:
        """获取对象"""
        with self.lock:
            if object_type not in self.pools:
                self.pools[object_type] = []
                self.weak_refs[object_type] = []
            
            # 尝试从池中获取对象
            pool = self.pools[object_type]
            if pool:
                obj = pool.pop()
                # 重置对象时间戳
                self.object_timestamps[id(obj)] = time.time()
                return obj
            
            # 创建新对象
            obj = factory_func()
            self.object_timestamps[id(obj)] = time.time()
            
            # 添加弱引用用于追踪
            weak_ref = weakref.ref(obj, lambda ref: self._on_object_deleted(ref, object_type))
            self.weak_refs[object_type].append(weak_ref)
            
            return obj
    
    def return_object(self, object_type: str, obj: Any):
        """归还对象"""
        with self.lock:
            if object_type not in self.pools:
                return
            
            pool = self.pools[object_type]
            if len(pool) < self.config.max_objects:
                # 清理对象状态
                self._reset_object(obj)
                pool.append(obj)
                self.object_timestamps[id(obj)] = time.time()
    
    def _reset_object(self, obj: Any):
        """重置对象状态"""
        if hasattr(obj, 'clear'):
            obj.clear()
        elif hasattr(obj, 'reset'):
            obj.reset()
        elif isinstance(obj, dict):
            obj.clear()
        elif isinstance(obj, list):
            obj.clear()
    
    def _on_object_deleted(self, weak_ref: weakref.ref, object_type: str):
        """对象被删除时的回调"""
        with self.lock:
            if object_type in self.weak_refs:
                try:
                    self.weak_refs[object_type].remove(weak_ref)
                except ValueError:
                    pass
    
    def _cleanup_worker(self):
        """清理工作线程"""
        while True:
            try:
                time.sleep(60)  # 每分钟清理一次
                self._cleanup_expired_objects()
            except Exception as e:
                print(f"对象池清理异常: {e}")
    
    def _cleanup_expired_objects(self):
        """清理过期对象"""
        current_time = time.time()
        
        with self.lock:
            total_objects = sum(len(pool) for pool in self.pools.values())
            if total_objects < self.config.max_objects * self.config.cleanup_threshold:
                return
            
            for object_type, pool in self.pools.items():
                expired_objects = []
                
                for obj in pool[:]:
                    obj_id = id(obj)
                    if obj_id in self.object_timestamps:
                        age = current_time - self.object_timestamps[obj_id]
                        if age > self.config.object_lifetime:
                            expired_objects.append(obj)
                
                # 移除过期对象
                for obj in expired_objects:
                    try:
                        pool.remove(obj)
                        obj_id = id(obj)
                        if obj_id in self.object_timestamps:
                            del self.object_timestamps[obj_id]
                    except ValueError:
                        pass
            
            # 强制垃圾回收
            if total_objects > self.config.max_objects * 0.9:
                gc.collect()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            stats = {
                'total_pools': len(self.pools),
                'pools': {}
            }
            
            for object_type, pool in self.pools.items():
                stats['pools'][object_type] = {
                    'size': len(pool),
                    'weak_refs': len(self.weak_refs.get(object_type, []))
                }
            
            stats['total_objects'] = sum(len(pool) for pool in self.pools.values())
            stats['total_timestamps'] = len(self.object_timestamps)
            
            return stats


class StreamWriter:
    """流式写入器"""
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.write_queue: Queue = Queue(maxsize=config.write_queue_size)
        self.writers: Dict[str, Any] = {}
        self.file_sizes: Dict[str, int] = {}
        self.file_counters: Dict[str, int] = {}
        self.lock = threading.Lock()
        
        # 启动异步写入线程
        if config.enable_async_write:
            self.write_thread = threading.Thread(target=self._write_worker, daemon=True)
            self.write_thread.start()
        else:
            self.write_thread = None
    
    def write_data(self, file_path: str, data: Any, format_type: str = 'json'):
        """写入数据"""
        if self.config.enable_async_write:
            try:
                self.write_queue.put({
                    'file_path': file_path,
                    'data': data,
                    'format_type': format_type,
                    'timestamp': time.time()
                }, timeout=1.0)
            except:
                # 队列满时同步写入
                self._write_data_sync(file_path, data, format_type)
        else:
            self._write_data_sync(file_path, data, format_type)
    
    def _write_data_sync(self, file_path: str, data: Any, format_type: str):
        """同步写入数据"""
        try:
            # 检查文件大小，必要时分割文件
            actual_path = self._get_actual_file_path(file_path)
            
            # 准备数据
            if format_type == 'json':
                content = json.dumps(data, ensure_ascii=False, indent=None)
            else:
                content = str(data)
            
            content += '\n'
            content_bytes = content.encode('utf-8')
            
            # 写入文件
            with self.lock:
                if actual_path.suffix == '.gz':
                    with gzip.open(actual_path, 'at', encoding='utf-8') as f:
                        f.write(content)
                else:
                    with open(actual_path, 'a', encoding='utf-8', buffering=self.config.buffer_size) as f:
                        f.write(content)
                
                # 更新文件大小
                if str(actual_path) not in self.file_sizes:
                    self.file_sizes[str(actual_path)] = 0
                self.file_sizes[str(actual_path)] += len(content_bytes)
                
        except Exception as e:
            print(f"写入文件失败 {file_path}: {e}")
    
    def _get_actual_file_path(self, file_path: str) -> Path:
        """获取实际文件路径（处理文件分割）"""
        path = Path(file_path)
        
        # 检查是否需要压缩
        if self.config.compression_level > 0 and not path.suffix == '.gz':
            path = path.with_suffix(path.suffix + '.gz')
        
        # 检查文件大小是否超限
        current_size = self.file_sizes.get(str(path), 0)
        max_size_bytes = self.config.max_file_size_mb * 1024 * 1024
        
        if current_size > max_size_bytes:
            # 需要分割文件
            base_name = path.stem
            if path.suffix == '.gz':
                base_name = base_name.rsplit('.', 1)[0]  # 去掉.json等扩展名
            
            counter = self.file_counters.get(str(path), 0) + 1
            self.file_counters[str(path)] = counter
            
            new_name = f"{base_name}_part{counter:03d}.json"
            if self.config.compression_level > 0:
                new_name += '.gz'
            
            path = path.parent / new_name
        
        # 确保目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        return path
    
    def _write_worker(self):
        """异步写入工作线程"""
        while True:
            try:
                # 获取写入任务
                task = self.write_queue.get(timeout=1.0)
                if task is None:  # 停止信号
                    break
                
                self._write_data_sync(
                    task['file_path'],
                    task['data'],
                    task['format_type']
                )
                
                self.write_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                print(f"异步写入异常: {e}")
    
    def flush_all(self):
        """刷新所有缓冲区"""
        if self.write_thread and self.write_thread.is_alive():
            # 等待队列清空
            self.write_queue.join()
    
    def close(self):
        """关闭写入器"""
        if self.write_thread and self.write_thread.is_alive():
            # 发送停止信号
            try:
                self.write_queue.put(None, timeout=1.0)
                self.write_thread.join(timeout=5.0)
            except:
                pass
        
        # 关闭所有文件
        with self.lock:
            for writer in self.writers.values():
                try:
                    if hasattr(writer, 'close'):
                        writer.close()
                except:
                    pass
            self.writers.clear()


class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self, max_memory_mb: int = 2048):
        self.max_memory_mb = max_memory_mb
        self.process = psutil.Process()
        self.object_pool = ObjectPool(MemoryPool())
        self.stream_writer = StreamWriter(StreamConfig())
        
        # 监控线程
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._memory_monitor, daemon=True)
        self.monitor_thread.start()
        
        # 统计信息
        self.gc_count = 0
        self.gc_freed_mb = 0.0
        self.peak_memory_mb = 0.0
    
    def get_memory_usage_mb(self) -> float:
        """获取当前内存使用量(MB)"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_memory_percent(self) -> float:
        """获取内存使用百分比"""
        return self.get_memory_usage_mb() / self.max_memory_mb
    
    def trigger_gc_if_needed(self) -> float:
        """如需要则触发垃圾回收"""
        memory_percent = self.get_memory_percent()
        
        if memory_percent > 0.8:  # 超过80%时触发
            return self.force_gc()
        return 0.0
    
    def force_gc(self) -> float:
        """强制垃圾回收"""
        before = self.get_memory_usage_mb()
        
        # 多轮垃圾回收
        for i in range(3):
            gc.collect()
        
        after = self.get_memory_usage_mb()
        freed = before - after
        
        self.gc_count += 1
        self.gc_freed_mb += freed
        
        return freed
    
    def optimize_for_large_scale(self, target_records: int) -> Dict[str, Any]:
        """为大规模数据生成优化内存"""
        recommendations = {
            'batch_size': min(50000, target_records // 20),
            'gc_frequency': max(1, target_records // 100000),
            'memory_warnings': [],
            'optimizations_applied': []
        }
        
        # 检查系统内存
        system_memory_gb = psutil.virtual_memory().total / 1024**3
        if system_memory_gb < 8:
            recommendations['memory_warnings'].append(
                f"系统内存仅{system_memory_gb:.1f}GB，建议至少8GB用于百万级数据生成"
            )
        
        # 调整垃圾回收策略
        gc.set_threshold(700, 10, 10)  # 更激进的GC策略
        recommendations['optimizations_applied'].append("调整垃圾回收阈值")
        
        # 预分配对象池
        self._preallocate_common_objects()
        recommendations['optimizations_applied'].append("预分配对象池")
        
        return recommendations
    
    def _preallocate_common_objects(self):
        """预分配常用对象"""
        # 预分配字典对象
        for _ in range(1000):
            self.object_pool.return_object('dict', {})
        
        # 预分配列表对象
        for _ in range(1000):
            self.object_pool.return_object('list', [])
    
    def _memory_monitor(self):
        """内存监控线程"""
        while self.monitoring:
            try:
                current_memory = self.get_memory_usage_mb()
                self.peak_memory_mb = max(self.peak_memory_mb, current_memory)
                
                # 内存使用超过90%时强制GC
                if current_memory / self.max_memory_mb > 0.9:
                    freed = self.force_gc()
                    if freed > 0:
                        print(f"🧹 内存告警触发GC，释放 {freed:.1f}MB")
                
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                print(f"内存监控异常: {e}")
                time.sleep(10)
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        return {
            'current_memory_mb': self.get_memory_usage_mb(),
            'peak_memory_mb': self.peak_memory_mb,
            'memory_usage_percent': self.get_memory_percent() * 100,
            'gc_count': self.gc_count,
            'total_gc_freed_mb': self.gc_freed_mb,
            'avg_gc_freed_mb': self.gc_freed_mb / max(1, self.gc_count),
            'object_pool_stats': self.object_pool.get_stats(),
            'write_queue_size': self.stream_writer.write_queue.qsize() if self.stream_writer.write_queue else 0
        }
    
    def create_optimized_data_iterator(self, data_generator: callable, 
                                     batch_size: int = 10000) -> Iterator[List[Any]]:
        """创建优化的数据迭代器"""
        batch = []
        
        for item in data_generator():
            batch.append(item)
            
            if len(batch) >= batch_size:
                yield batch
                batch.clear()
                
                # 定期触发GC
                if len(batch) % (batch_size * 5) == 0:
                    self.trigger_gc_if_needed()
        
        # 处理最后一批数据
        if batch:
            yield batch
    
    def write_incrementally(self, file_path: str, data: Any, format_type: str = 'json'):
        """增量写入数据"""
        self.stream_writer.write_data(file_path, data, format_type)
    
    def cleanup(self):
        """清理资源"""
        self.monitoring = False
        
        # 等待监控线程结束
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        # 关闭流写入器
        self.stream_writer.flush_all()
        self.stream_writer.close()
        
        # 最终垃圾回收
        self.force_gc()