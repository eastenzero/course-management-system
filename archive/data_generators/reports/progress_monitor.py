#!/usr/bin/env python
"""
进度监控系统 - 为百万级数据导入提供详细的进度可视化
包含进度条、内存监控、性能统计和实时状态反馈
"""

import time
import gc
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from collections import deque
import sys
import os

# 尝试导入rich库用于更好的进度显示
try:
    from rich.console import Console
    from rich.progress import Progress, TaskID, BarColumn, TextColumn, TimeRemainingColumn, MofNCompleteColumn
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

@dataclass
class ProgressStats:
    """进度统计数据"""
    start_time: float
    current_count: int
    total_count: int
    speed_history: deque
    error_count: int
    last_update_time: float
    
    def __post_init__(self):
        if not hasattr(self, 'speed_history') or self.speed_history is None:
            self.speed_history = deque(maxlen=10)  # 保存最近10次的速度记录

class ProgressTracker:
    """进度跟踪器 - 跟踪单个操作的进度"""
    
    def __init__(self, operation_name: str, total_count: int):
        self.operation_name = operation_name
        self.total_count = total_count
        self.current_count = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.speed_history = deque(maxlen=10)  # 保存最近10次的速度记录
        self.error_count = 0
        
    def update(self, current_count: int, error_count: int = 0):
        """更新进度"""
        current_time = time.time()
        
        # 计算速度（基于最近的更新）
        if self.current_count > 0:
            time_diff = current_time - self.last_update_time
            count_diff = current_count - self.current_count
            if time_diff > 0:
                speed = count_diff / time_diff
                self.speed_history.append(speed)
        
        self.current_count = current_count
        self.error_count = error_count
        self.last_update_time = current_time
    
    def get_progress_info(self) -> Dict[str, Any]:
        """获取进度信息"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # 计算平均速度
        if self.speed_history:
            avg_speed = sum(self.speed_history) / len(self.speed_history)
        else:
            avg_speed = self.current_count / elapsed_time if elapsed_time > 0 else 0
        
        # 计算预计剩余时间
        remaining_count = self.total_count - self.current_count
        eta_seconds = remaining_count / avg_speed if avg_speed > 0 else 0
        
        # 计算进度百分比
        progress_percentage = (self.current_count / self.total_count * 100) if self.total_count > 0 else 0
        
        return {
            'operation_name': self.operation_name,
            'current_count': self.current_count,
            'total_count': self.total_count,
            'progress_percentage': progress_percentage,
            'elapsed_time': elapsed_time,
            'eta_seconds': eta_seconds,
            'avg_speed': avg_speed,
            'current_speed': self.speed_history[-1] if self.speed_history else 0,
            'error_count': self.error_count,
        }

class MemoryMonitor:
    """内存监控器 - 监控内存使用情况并提供优化建议"""
    
    def __init__(self, max_memory_gb: float = 2.0, warning_threshold: float = 0.7):
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.warning_threshold = warning_threshold
        self.danger_threshold = 0.85
        self.critical_threshold = 0.95
        self.current_usage = 0
        self.peak_usage = 0
        self.gc_count = 0
        
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存使用信息"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            self.current_usage = memory_info.rss
            
            # 更新峰值使用量
            if self.current_usage > self.peak_usage:
                self.peak_usage = self.current_usage
            
            usage_ratio = self.current_usage / self.max_memory_bytes
            
            # 确定内存状态
            if usage_ratio >= self.critical_threshold:
                status = "CRITICAL"
                color = "red"
            elif usage_ratio >= self.danger_threshold:
                status = "DANGER"
                color = "yellow"
            elif usage_ratio >= self.warning_threshold:
                status = "WARNING"
                color = "orange"
            else:
                status = "NORMAL"
                color = "green"
            
            return {
                'current_mb': self.current_usage / (1024 * 1024),
                'max_mb': self.max_memory_bytes / (1024 * 1024),
                'peak_mb': self.peak_usage / (1024 * 1024),
                'usage_ratio': usage_ratio,
                'usage_percentage': usage_ratio * 100,
                'status': status,
                'color': color,
                'gc_count': self.gc_count,
                'should_gc': usage_ratio >= self.danger_threshold
            }
        except Exception as e:
            return {
                'current_mb': 0,
                'max_mb': self.max_memory_bytes / (1024 * 1024),
                'peak_mb': 0,
                'usage_ratio': 0,
                'usage_percentage': 0,
                'status': "ERROR",
                'color': "red",
                'gc_count': self.gc_count,
                'should_gc': False,
                'error': str(e)
            }
    
    def force_garbage_collection(self):
        """强制执行垃圾回收"""
        gc.collect()
        self.gc_count += 1
    
    def optimize_batch_size(self, current_batch_size: int) -> int:
        """根据内存使用情况优化批次大小"""
        memory_info = self.get_memory_info()
        usage_ratio = memory_info['usage_ratio']
        
        if usage_ratio >= self.critical_threshold:
            # 内存使用过高，大幅减少批次大小
            return max(100, current_batch_size // 4)
        elif usage_ratio >= self.danger_threshold:
            # 内存使用偏高，减少批次大小
            return max(500, current_batch_size // 2)
        elif usage_ratio >= self.warning_threshold:
            # 内存使用正常偏高，略微减少批次大小
            return max(1000, int(current_batch_size * 0.8))
        elif usage_ratio < 0.5:
            # 内存使用较低，可以增加批次大小
            return min(50000, int(current_batch_size * 1.5))
        else:
            # 内存使用正常，保持当前批次大小
            return current_batch_size

class EnhancedProgressBar:
    """增强型进度条 - 支持Rich和基础文本两种显示方式"""
    
    def __init__(self, use_rich: bool = RICH_AVAILABLE):
        self.use_rich = use_rich and RICH_AVAILABLE
        self.console = Console() if self.use_rich else None
        self.rich_progress = None
        self.tasks = {}  # 存储Rich进度任务ID
        self.last_display_time = 0
        self.display_interval = 0.5  # 更新间隔（秒）
        
        if self.use_rich:
            self._init_rich_progress()
    
    def _init_rich_progress(self):
        """初始化Rich进度条"""
        if not self.use_rich:
            return
            
        self.rich_progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            MofNCompleteColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            TimeRemainingColumn(),
            console=self.console,
            expand=True
        )
    
    def add_task(self, task_name: str, total: int) -> Optional[TaskID]:
        """添加新的进度任务"""
        if self.use_rich and self.rich_progress:
            task_id = self.rich_progress.add_task(task_name, total=total)
            self.tasks[task_name] = task_id
            return task_id
        return None
    
    def update_task(self, task_name: str, current: int):
        """更新任务进度"""
        current_time = time.time()
        
        # 控制更新频率，避免过于频繁的显示更新
        if current_time - self.last_display_time < self.display_interval:
            return
        
        if self.use_rich and self.rich_progress and task_name in self.tasks:
            task_id = self.tasks[task_name]
            self.rich_progress.update(task_id, completed=current)
        else:
            self._display_text_progress(task_name, current)
        
        self.last_display_time = current_time
    
    def _display_text_progress(self, task_name: str, current: int):
        """显示文本进度条（fallback方式）"""
        # 简单的文本进度条
        bar_length = 50
        progress = current / 100000  # 假设总数，实际使用时需要传入total
        filled_length = int(bar_length * min(progress, 1.0))
        
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f'\r{task_name}: |{bar}| {current:,} ', end='', flush=True)
    
    def start(self):
        """开始进度显示"""
        if self.use_rich and self.rich_progress:
            self.rich_progress.start()
    
    def stop(self):
        """停止进度显示"""
        if self.use_rich and self.rich_progress:
            self.rich_progress.stop()

class ImportProgressManager:
    """导入进度管理器 - 统一管理所有导入操作的进度"""
    
    def __init__(self, max_memory_gb: float = 2.0):
        self.trackers: Dict[str, ProgressTracker] = {}
        self.memory_monitor = MemoryMonitor(max_memory_gb)
        self.progress_bar = EnhancedProgressBar()
        self.start_time = time.time()
        self.is_running = False
        self.display_thread = None
        self.stop_display = False
        
        # 操作阶段定义
        self.operation_phases = [
            "数据加载",
            "学生用户创建", 
            "教师用户创建",
            "学生档案创建",
            "教师档案创建", 
            "课程创建",
            "选课记录创建"
        ]
        
        self.current_phase = 0
        
    def register_operation(self, operation_name: str, total_count: int):
        """注册一个新的操作"""
        tracker = ProgressTracker(operation_name, total_count)
        self.trackers[operation_name] = tracker
        
        # 添加到进度条
        if self.progress_bar:
            self.progress_bar.add_task(operation_name, total_count)
        
        print(f"\n📋 注册操作: {operation_name} (总计: {total_count:,} 项)")
        
    def update_progress(self, operation_name: str, current_count: int, error_count: int = 0):
        """更新操作进度"""
        if operation_name in self.trackers:
            tracker = self.trackers[operation_name]
            tracker.update(current_count, error_count)
            
            # 更新进度条
            if self.progress_bar:
                self.progress_bar.update_task(operation_name, current_count)
            
            # 检查内存使用情况
            memory_info = self.memory_monitor.get_memory_info()
            if memory_info['should_gc']:
                print(f"\n⚠️ 内存使用过高 ({memory_info['usage_percentage']:.1f}%)，执行垃圾回收...")
                self.memory_monitor.force_garbage_collection()
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """获取总体进度信息"""
        if not self.trackers:
            return {}
        
        total_items = sum(tracker.total_count for tracker in self.trackers.values())
        completed_items = sum(tracker.current_count for tracker in self.trackers.values())
        total_errors = sum(tracker.error_count for tracker in self.trackers.values())
        
        overall_percentage = (completed_items / total_items * 100) if total_items > 0 else 0
        elapsed_time = time.time() - self.start_time
        
        # 计算总体速度
        overall_speed = completed_items / elapsed_time if elapsed_time > 0 else 0
        remaining_items = total_items - completed_items
        eta_seconds = remaining_items / overall_speed if overall_speed > 0 else 0
        
        return {
            'total_items': total_items,
            'completed_items': completed_items,
            'remaining_items': remaining_items,
            'overall_percentage': overall_percentage,
            'elapsed_time': elapsed_time,
            'eta_seconds': eta_seconds,
            'overall_speed': overall_speed,
            'total_errors': total_errors,
            'memory_info': self.memory_monitor.get_memory_info()
        }
    
    def display_detailed_status(self):
        """显示详细状态信息"""
        overall_progress = self.get_overall_progress()
        
        if not overall_progress:
            return
        
        print("\n" + "=" * 80)
        print("📊 详细进度报告")
        print("=" * 80)
        
        # 总体进度
        print(f"🎯 总体进度: {overall_progress['completed_items']:,}/{overall_progress['total_items']:,} "
              f"({overall_progress['overall_percentage']:.1f}%)")
        
        # 时间信息
        elapsed_str = str(timedelta(seconds=int(overall_progress['elapsed_time'])))
        eta_str = str(timedelta(seconds=int(overall_progress['eta_seconds']))) if overall_progress['eta_seconds'] > 0 else "计算中..."
        print(f"⏱️ 已用时间: {elapsed_str} | 预计剩余: {eta_str}")
        
        # 性能信息
        print(f"🚀 处理速度: {overall_progress['overall_speed']:.0f} 条/秒")
        print(f"❌ 错误数量: {overall_progress['total_errors']:,}")
        
        # 内存信息
        memory_info = overall_progress['memory_info']
        memory_status_icon = {
            'NORMAL': '🟢',
            'WARNING': '🟡', 
            'DANGER': '🟠',
            'CRITICAL': '🔴',
            'ERROR': '❌'
        }.get(memory_info['status'], '❓')
        
        print(f"{memory_status_icon} 内存使用: {memory_info['current_mb']:.1f}MB / "
              f"{memory_info['max_mb']:.1f}MB ({memory_info['usage_percentage']:.1f}%)")
        
        # 各操作详细进度
        print("\n📋 操作详情:")
        for name, tracker in self.trackers.items():
            info = tracker.get_progress_info()
            status_bar = self._create_text_progress_bar(info['progress_percentage'])
            print(f"   {status_bar} {name}: {info['current_count']:,}/{info['total_count']:,} "
                  f"({info['progress_percentage']:.1f}%) - {info['avg_speed']:.0f} 条/秒")
        
        print("=" * 80)
    
    def _create_text_progress_bar(self, percentage: float, length: int = 20) -> str:
        """创建文本进度条"""
        filled_length = int(length * percentage / 100)
        bar = '█' * filled_length + '░' * (length - filled_length)
        return f'[{bar}]'
    
    def start_monitoring(self):
        """开始监控"""
        self.is_running = True
        if self.progress_bar:
            self.progress_bar.start()
        
        # 启动后台显示线程
        self.stop_display = False
        self.display_thread = threading.Thread(target=self._background_display)
        self.display_thread.daemon = True
        self.display_thread.start()
        
        print("🚀 进度监控系统已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        self.stop_display = True
        
        if self.display_thread:
            self.display_thread.join(timeout=2)
        
        if self.progress_bar:
            self.progress_bar.stop()
        
        # 显示最终报告
        self.display_final_report()
    
    def _background_display(self):
        """后台显示线程"""
        while not self.stop_display and self.is_running:
            time.sleep(5)  # 每5秒更新一次详细状态
            if not self.stop_display:
                self.display_detailed_status()
    
    def display_final_report(self):
        """显示最终报告"""
        overall_progress = self.get_overall_progress()
        
        if not overall_progress:
            return
        
        print("\n" + "🎉" * 20)
        print("📊 最终导入报告")
        print("🎉" * 20)
        
        # 总体统计
        total_time = overall_progress['elapsed_time']
        total_items = overall_progress['completed_items']
        avg_speed = total_items / total_time if total_time > 0 else 0
        
        print(f"✅ 导入完成: {total_items:,} 条记录")
        print(f"⏱️ 总用时: {str(timedelta(seconds=int(total_time)))}")
        print(f"🚀 平均速度: {avg_speed:.0f} 条/秒")
        print(f"❌ 总错误数: {overall_progress['total_errors']:,}")
        
        # 内存使用统计
        memory_info = overall_progress['memory_info']
        print(f"💾 峰值内存: {memory_info['peak_mb']:.1f}MB")
        print(f"🗑️ 垃圾回收次数: {memory_info['gc_count']}")
        
        # 各操作统计
        print("\n📋 操作统计:")
        for name, tracker in self.trackers.items():
            info = tracker.get_progress_info()
            success_rate = ((info['current_count'] - info['error_count']) / info['current_count'] * 100) if info['current_count'] > 0 else 100
            print(f"   📌 {name}: {info['current_count']:,}/{info['total_count']:,} "
                  f"(成功率: {success_rate:.1f}%)")
        
        print("🎉" * 20)
    
    def get_optimized_batch_size(self, current_batch_size: int) -> int:
        """获取优化的批次大小"""
        return self.memory_monitor.optimize_batch_size(current_batch_size)
    
    def should_force_gc(self) -> bool:
        """是否应该强制垃圾回收"""
        memory_info = self.memory_monitor.get_memory_info()
        return memory_info['should_gc']
    
    def force_gc(self):
        """强制垃圾回收"""
        self.memory_monitor.force_garbage_collection()
        print(f"🗑️ 执行垃圾回收 (第{self.memory_monitor.gc_count}次)")

def create_progress_manager(max_memory_gb: float = 2.0) -> ImportProgressManager:
    """创建进度管理器的工厂函数"""
    return ImportProgressManager(max_memory_gb)

# 安装依赖建议
def check_and_suggest_dependencies():
    """检查并建议安装依赖"""
    missing_deps = []
    
    try:
        import rich
    except ImportError:
        missing_deps.append("rich")
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    if missing_deps:
        print("⚠️ 建议安装以下依赖以获得更好的进度显示效果:")
        print("pip install " + " ".join(missing_deps))
        print()

if __name__ == "__main__":
    # 演示用法
    check_and_suggest_dependencies()
    
    # 创建进度管理器
    manager = create_progress_manager()
    
    # 演示进度监控
    print("🎬 进度监控系统演示")
    
    manager.start_monitoring()
    
    # 模拟一些操作
    manager.register_operation("演示操作1", 1000)
    manager.register_operation("演示操作2", 500)
    
    # 模拟进度更新
    for i in range(1001):
        manager.update_progress("演示操作1", i)
        time.sleep(0.01)
        
        if i % 2 == 0 and i <= 500:
            manager.update_progress("演示操作2", i // 2)
    
    manager.stop_monitoring()