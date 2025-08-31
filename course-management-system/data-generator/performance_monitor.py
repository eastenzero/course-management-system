# file: data-generator/performance_monitor.py
# 功能: 性能监控工具

import time
import psutil
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import pandas as pd
from collections import deque


@dataclass
class PerformanceSnapshot:
    """性能快照"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float
    active_threads: int
    generation_speed: float = 0.0  # 记录/秒
    processed_records: int = 0
    error_count: int = 0


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.snapshots: deque = deque(maxlen=history_size)
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.update_interval = 2.0  # 2秒更新一次
        
        # 基准值
        self.baseline_snapshot: Optional[PerformanceSnapshot] = None
        
        # 统计信息
        self.peak_cpu = 0.0
        self.peak_memory = 0.0
        self.total_errors = 0
        self.start_time: Optional[float] = None
        
        # 告警阈值
        self.cpu_threshold = 90.0
        self.memory_threshold = 90.0
        self.disk_threshold = 90.0
        
        # 告警回调
        self.alert_callbacks: List[callable] = []
    
    def start_monitoring(self):
        """开始监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.start_time = time.time()
        
        # 记录基准快照
        self.baseline_snapshot = self._capture_snapshot()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        print("📊 性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=3.0)
        
        print("📊 性能监控已停止")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 捕获性能快照
                snapshot = self._capture_snapshot()
                self.snapshots.append(snapshot)
                
                # 更新峰值统计
                self.peak_cpu = max(self.peak_cpu, snapshot.cpu_percent)
                self.peak_memory = max(self.peak_memory, snapshot.memory_percent)
                
                # 检查告警条件
                self._check_alerts(snapshot)
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"性能监控异常: {e}")
                time.sleep(5)
    
    def _capture_snapshot(self) -> PerformanceSnapshot:
        """捕获性能快照"""
        try:
            # CPU和内存
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            # 磁盘I/O
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / 1024 / 1024 if disk_io else 0
            disk_write_mb = disk_io.write_bytes / 1024 / 1024 if disk_io else 0
            
            # 网络I/O
            net_io = psutil.net_io_counters()
            net_sent_mb = net_io.bytes_sent / 1024 / 1024 if net_io else 0
            net_recv_mb = net_io.bytes_recv / 1024 / 1024 if net_io else 0
            
            # 线程数
            active_threads = threading.active_count()
            
            return PerformanceSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                disk_io_read_mb=disk_read_mb,
                disk_io_write_mb=disk_write_mb,
                network_io_sent_mb=net_sent_mb,
                network_io_recv_mb=net_recv_mb,
                active_threads=active_threads
            )
            
        except Exception as e:
            print(f"捕获性能快照失败: {e}")
            return PerformanceSnapshot(timestamp=time.time(), cpu_percent=0, memory_percent=0, memory_used_mb=0,
                                     disk_io_read_mb=0, disk_io_write_mb=0, network_io_sent_mb=0, 
                                     network_io_recv_mb=0, active_threads=0)
    
    def _check_alerts(self, snapshot: PerformanceSnapshot):
        """检查告警条件"""
        alerts = []
        
        if snapshot.cpu_percent > self.cpu_threshold:
            alerts.append(f"CPU使用率过高: {snapshot.cpu_percent:.1f}%")
        
        if snapshot.memory_percent > self.memory_threshold:
            alerts.append(f"内存使用率过高: {snapshot.memory_percent:.1f}%")
        
        # 检查磁盘空间
        try:
            disk_usage = psutil.disk_usage('.')
            if disk_usage.percent > self.disk_threshold:
                alerts.append(f"磁盘空间不足: {disk_usage.percent:.1f}%")
        except:
            pass
        
        # 触发告警回调
        for alert in alerts:
            print(f"⚠️ 性能告警: {alert}")
            for callback in self.alert_callbacks:
                try:
                    callback(alert, snapshot)
                except:
                    pass
    
    def update_generation_metrics(self, processed_records: int, error_count: int = 0):
        """更新生成指标"""
        if not self.snapshots:
            return
        
        current_snapshot = self.snapshots[-1]
        current_snapshot.processed_records = processed_records
        current_snapshot.error_count = error_count
        
        # 计算生成速度
        if len(self.snapshots) >= 2:
            prev_snapshot = self.snapshots[-2]
            time_diff = current_snapshot.timestamp - prev_snapshot.timestamp
            record_diff = processed_records - prev_snapshot.processed_records
            
            if time_diff > 0:
                current_snapshot.generation_speed = record_diff / time_diff
        
        self.total_errors = error_count
    
    def add_alert_callback(self, callback: callable):
        """添加告警回调"""
        self.alert_callbacks.append(callback)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """获取当前统计信息"""
        if not self.snapshots:
            return {}
        
        current = self.snapshots[-1]
        elapsed_time = time.time() - (self.start_time or time.time())
        
        return {
            'current_snapshot': asdict(current),
            'peak_cpu': self.peak_cpu,
            'peak_memory': self.peak_memory,
            'total_errors': self.total_errors,
            'elapsed_time': elapsed_time,
            'avg_cpu': self._calculate_average('cpu_percent'),
            'avg_memory': self._calculate_average('memory_percent'),
            'avg_generation_speed': self._calculate_average('generation_speed'),
            'snapshot_count': len(self.snapshots)
        }
    
    def _calculate_average(self, field: str) -> float:
        """计算字段平均值"""
        if not self.snapshots:
            return 0.0
        
        values = [getattr(snapshot, field) for snapshot in self.snapshots]
        return sum(values) / len(values)
    
    def get_performance_trends(self) -> Dict[str, List[float]]:
        """获取性能趋势"""
        if not self.snapshots:
            return {}
        
        trends = {
            'timestamps': [s.timestamp for s in self.snapshots],
            'cpu_percent': [s.cpu_percent for s in self.snapshots],
            'memory_percent': [s.memory_percent for s in self.snapshots],
            'memory_used_mb': [s.memory_used_mb for s in self.snapshots],
            'generation_speed': [s.generation_speed for s in self.snapshots],
            'processed_records': [s.processed_records for s in self.snapshots],
            'active_threads': [s.active_threads for s in self.snapshots]
        }
        
        return trends
    
    def export_performance_data(self, output_file: str = "performance_data.json"):
        """导出性能数据"""
        try:
            data = {
                'monitoring_info': {
                    'start_time': self.start_time,
                    'end_time': time.time(),
                    'total_snapshots': len(self.snapshots),
                    'update_interval': self.update_interval
                },
                'baseline_snapshot': asdict(self.baseline_snapshot) if self.baseline_snapshot else None,
                'performance_stats': self.get_current_stats(),
                'trends': self.get_performance_trends(),
                'snapshots': [asdict(snapshot) for snapshot in self.snapshots]
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"📊 性能数据已导出到: {output_file}")
            
        except Exception as e:
            print(f"导出性能数据失败: {e}")
    
    def generate_performance_report(self, output_dir: str = "performance_reports"):
        """生成性能报告"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # 生成JSON报告
            self.export_performance_data(str(output_path / "performance_data.json"))
            
            # 生成可视化图表
            self._generate_performance_charts(output_path)
            
            # 生成文本报告
            self._generate_text_report(output_path)
            
            print(f"📊 性能报告已生成到: {output_dir}")
            
        except Exception as e:
            print(f"生成性能报告失败: {e}")
    
    def _generate_performance_charts(self, output_path: Path):
        """生成性能图表"""
        try:
            trends = self.get_performance_trends()
            
            if not trends['timestamps']:
                return
            
            # 转换时间戳为相对时间
            start_time = trends['timestamps'][0]
            relative_times = [(t - start_time) / 60 for t in trends['timestamps']]  # 转换为分钟
            
            # 创建子图
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('百万级数据生成性能监控报告', fontsize=16)
            
            # CPU使用率
            axes[0, 0].plot(relative_times, trends['cpu_percent'], 'b-', linewidth=2)
            axes[0, 0].set_title('CPU使用率 (%)')
            axes[0, 0].set_xlabel('时间 (分钟)')
            axes[0, 0].set_ylabel('CPU %')
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].axhline(y=self.cpu_threshold, color='r', linestyle='--', alpha=0.7, label='告警阈值')
            axes[0, 0].legend()
            
            # 内存使用率
            axes[0, 1].plot(relative_times, trends['memory_percent'], 'g-', linewidth=2)
            axes[0, 1].set_title('内存使用率 (%)')
            axes[0, 1].set_xlabel('时间 (分钟)')
            axes[0, 1].set_ylabel('内存 %')
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].axhline(y=self.memory_threshold, color='r', linestyle='--', alpha=0.7, label='告警阈值')
            axes[0, 1].legend()
            
            # 数据生成速度
            axes[1, 0].plot(relative_times, trends['generation_speed'], 'm-', linewidth=2)
            axes[1, 0].set_title('数据生成速度 (记录/秒)')
            axes[1, 0].set_xlabel('时间 (分钟)')
            axes[1, 0].set_ylabel('记录/秒')
            axes[1, 0].grid(True, alpha=0.3)
            
            # 累计处理记录数
            axes[1, 1].plot(relative_times, trends['processed_records'], 'c-', linewidth=2)
            axes[1, 1].set_title('累计处理记录数')
            axes[1, 1].set_xlabel('时间 (分钟)')
            axes[1, 1].set_ylabel('记录数')
            axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path / "performance_charts.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"生成性能图表失败: {e}")
    
    def _generate_text_report(self, output_path: Path):
        """生成文本报告"""
        try:
            stats = self.get_current_stats()
            
            report_lines = [
                "百万级数据生成性能监控报告",
                "=" * 50,
                "",
                f"监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"监控持续时间: {stats.get('elapsed_time', 0):.1f} 秒",
                f"性能快照数量: {stats.get('snapshot_count', 0)}",
                "",
                "== 性能峰值 ==",
                f"CPU峰值使用率: {self.peak_cpu:.1f}%",
                f"内存峰值使用率: {self.peak_memory:.1f}%",
                "",
                "== 平均性能 ==",
                f"平均CPU使用率: {stats.get('avg_cpu', 0):.1f}%",
                f"平均内存使用率: {stats.get('avg_memory', 0):.1f}%",
                f"平均生成速度: {stats.get('avg_generation_speed', 0):.0f} 记录/秒",
                "",
                "== 当前状态 ==",
            ]
            
            current = stats.get('current_snapshot', {})
            if current:
                report_lines.extend([
                    f"当前CPU使用率: {current.get('cpu_percent', 0):.1f}%",
                    f"当前内存使用率: {current.get('memory_percent', 0):.1f}%",
                    f"当前内存使用量: {current.get('memory_used_mb', 0):.0f}MB",
                    f"当前活动线程数: {current.get('active_threads', 0)}",
                    f"已处理记录数: {current.get('processed_records', 0):,}",
                    f"错误总数: {self.total_errors}",
                ])
            
            report_lines.extend([
                "",
                "== 性能建议 ==",
                self._generate_performance_recommendations(stats)
            ])
            
            # 写入报告文件
            with open(output_path / "performance_report.txt", 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
        except Exception as e:
            print(f"生成文本报告失败: {e}")
    
    def _generate_performance_recommendations(self, stats: Dict[str, Any]) -> str:
        """生成性能建议"""
        recommendations = []
        
        avg_cpu = stats.get('avg_cpu', 0)
        avg_memory = stats.get('avg_memory', 0)
        avg_speed = stats.get('avg_generation_speed', 0)
        
        if avg_cpu > 80:
            recommendations.append("- CPU使用率较高，建议减少并行度或优化计算密集型操作")
        
        if avg_memory > 80:
            recommendations.append("- 内存使用率较高，建议减少批次大小或启用更积极的垃圾回收")
        
        if avg_speed < 100:
            recommendations.append("- 数据生成速度较慢，建议增加并行度或优化生成算法")
        
        if self.total_errors > 0:
            recommendations.append(f"- 检测到 {self.total_errors} 个错误，建议检查错误日志并修复问题")
        
        if not recommendations:
            recommendations.append("- 性能表现良好，无特殊建议")
        
        return '\n'.join(recommendations)
    
    def print_realtime_stats(self):
        """实时打印统计信息"""
        if not self.snapshots:
            print("暂无性能数据")
            return
        
        current = self.snapshots[-1]
        
        print(f"\n📊 实时性能状态 [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"{'='*50}")
        print(f"🖥️ CPU: {current.cpu_percent:5.1f}%  💾 内存: {current.memory_percent:5.1f}% ({current.memory_used_mb:,.0f}MB)")
        print(f"🚀 生成速度: {current.generation_speed:6.0f} 条/秒")
        print(f"📈 已处理: {current.processed_records:,} 条记录")
        print(f"🧵 活动线程: {current.active_threads} 个")
        
        if self.total_errors > 0:
            print(f"❌ 错误总数: {self.total_errors}")
        
        print(f"{'='*50}")


def create_performance_dashboard():
    """创建性能监控仪表板"""
    monitor = PerformanceMonitor(history_size=500)
    
    def alert_handler(alert_message: str, snapshot):
        """告警处理器"""
        print(f"🚨 {alert_message}")
    
    monitor.add_alert_callback(alert_handler)
    return monitor


if __name__ == "__main__":
    # 示例使用
    monitor = create_performance_dashboard()
    monitor.start_monitoring()
    
    try:
        # 模拟数据生成过程
        for i in range(100):
            time.sleep(1)
            monitor.update_generation_metrics(i * 1000)
            
            if i % 10 == 0:
                monitor.print_realtime_stats()
    
    finally:
        monitor.stop_monitoring()
        monitor.generate_performance_report()