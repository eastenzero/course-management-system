# file: data-generator/mega_scale/__init__.py
# 功能: 百万级数据生成系统包初始化

from .batch_manager import BatchProcessingManager, BatchConfig
from .memory_optimizer import MemoryOptimizer, StreamConfig
from .parallel_engine import ParallelComputingEngine, TaskConfig
from .progress_monitor import ProgressMonitor
from .mega_generator import MegaDataGenerator

__all__ = [
    'BatchProcessingManager',
    'BatchConfig', 
    'MemoryOptimizer',
    'StreamConfig',
    'ParallelComputingEngine',
    'TaskConfig',
    'ProgressMonitor',
    'MegaDataGenerator'
]

__version__ = "1.0.0"