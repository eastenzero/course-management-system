#!/usr/bin/env python
"""
简化版进度监控测试
"""

import time
import sys
import os

def simple_progress_bar(current, total, width=50):
    """创建简单的文本进度条"""
    if total == 0:
        return "[" + "=" * width + "] 100.0%"
    
    percentage = current / total
    filled_length = int(width * percentage)
    bar = "█" * filled_length + "░" * (width - filled_length)
    return f"[{bar}] {percentage*100:6.2f}%"

def simulate_import():
    """模拟数据导入进度"""
    print("🚀 简化版进度监控测试")
    print("=" * 60)
    
    operations = [
        ("学生用户创建", 5000),
        ("教师用户创建", 500), 
        ("课程创建", 1200),
        ("选课记录创建", 8000)
    ]
    
    for op_name, total_count in operations:
        print(f"\n📋 {op_name} (总计: {total_count:,} 项)")
        
        batch_size = 100
        for i in range(0, total_count, batch_size):
            current = min(i + batch_size, total_count)
            
            # 创建进度条
            progress_bar = simple_progress_bar(current, total_count)
            speed = current / ((time.time() % 100) + 1)  # 模拟速度
            
            # 显示进度
            print(f"\r   {progress_bar} {current:,}/{total_count:,} ({speed:.0f} 条/秒)", end="", flush=True)
            
            # 模拟处理时间
            time.sleep(0.01)
        
        print(f"\n   ✅ {op_name} 完成")
    
    print("\n🎉 所有导入操作完成！")

if __name__ == "__main__":
    simulate_import()