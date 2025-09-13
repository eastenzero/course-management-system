#!/usr/bin/env python
"""
进度监控系统测试脚本
验证进度条、内存监控和性能统计功能
"""

import time
import random
from progress_monitor import create_progress_manager

def simulate_data_import():
    """模拟数据导入过程"""
    print("🚀 进度监控系统测试开始")
    print("=" * 60)
    
    # 创建进度管理器
    manager = create_progress_manager(max_memory_gb=2.0)
    
    try:
        # 启动监控
        manager.start_monitoring()
        
        # 模拟多个操作
        operations = [
            ("学生用户创建", 5000),
            ("教师用户创建", 500), 
            ("课程创建", 1200),
            ("选课记录创建", 8000)
        ]
        
        for op_name, total_count in operations:
            print(f"\n📋 开始 {op_name}...")
            
            # 注册操作
            manager.register_operation(op_name, total_count)
            
            # 模拟批量处理
            batch_size = 100
            for i in range(0, total_count, batch_size):
                current = min(i + batch_size, total_count)
                
                # 模拟处理时间
                time.sleep(0.01)
                
                # 模拟错误
                error_count = random.randint(0, 2) if random.random() < 0.1 else 0
                
                # 更新进度
                manager.update_progress(op_name, current, error_count)
                
                # 模拟内存压力
                if i % 1000 == 0 and manager.should_force_gc():
                    manager.force_gc()
        
        print(f"\n✅ 所有操作完成")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
    finally:
        # 停止监控
        manager.stop_monitoring()
    
    print("🎉 进度监控系统测试完成")

if __name__ == "__main__":
    simulate_data_import()