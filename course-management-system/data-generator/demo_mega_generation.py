# file: demo_mega_generation.py
# 功能: 百万级数据生成系统演示

import time
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

def demo_small_scale():
    """演示小规模数据生成"""
    print("🎬 演示1: 小规模数据生成")
    print("-" * 50)
    
    try:
        from mega_scale.mega_generator import MegaDataGenerator, MegaGenerationConfig
        
        # 小规模配置 - 适合演示
        config = MegaGenerationConfig(
            target_records=1000,    # 1千条记录
            batch_size=200,         # 200条/批次
            max_memory_mb=256,      # 256MB内存限制
            max_workers=2,          # 2个工作进程
            enable_compression=False,
            enable_streaming=True,
            output_formats=['json']
        )
        
        print(f"   📊 配置: {config.target_records:,} 条记录, {config.batch_size} 条/批次")
        
        # 创建生成器
        generator = MegaDataGenerator(config)
        
        print("   🚀 开始生成数据...")
        start_time = time.time()
        
        # 执行生成（使用small规模避免长时间运行）
        results = generator.generate_mega_dataset(
            scale='small',  # 使用small规模
            output_dir='demo_output',
            conflict_difficulty='simple'
        )
        
        end_time = time.time()
        
        if results and results.get('success'):
            stats = results.get('performance_stats', {})
            total_records = stats.get('total_records', 0)
            
            print(f"   ✅ 生成成功!")
            print(f"   📊 实际记录数: {total_records:,}")
            print(f"   ⏱️ 耗时: {end_time - start_time:.1f} 秒")
            print(f"   🚀 平均速度: {total_records/(end_time - start_time):.0f} 条/秒")
            
            # 显示性能统计
            memory_stats = stats.get('memory_stats', {})
            if memory_stats:
                print(f"   💾 峰值内存: {memory_stats.get('peak_memory_mb', 0):.0f}MB")
                print(f"   🧹 GC次数: {memory_stats.get('gc_count', 0)}")
            
            print(f"   📁 输出位置: demo_output/")
            return True
        else:
            print("   ❌ 生成失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 演示失败: {e}")
        return False


def demo_configuration():
    """演示配置系统"""
    print("\n🎬 演示2: 配置系统验证")
    print("-" * 50)
    
    try:
        import yaml
        
        # 加载配置文件
        config_file = "mega_scale_config.yml"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("   ✅ 配置文件加载成功")
        
        # 验证关键配置项
        print("   📋 关键配置项验证:")
        
        # 基本配置
        generation = config.get('generation', {})
        print(f"   - 目标记录数: {generation.get('target_records', 'N/A'):,}")
        print(f"   - 数据规模: {generation.get('scale', 'N/A')}")
        
        # 批处理配置
        batch = config.get('batch_processing', {})
        print(f"   - 批次大小: {batch.get('batch_size', 'N/A'):,}")
        print(f"   - 最大工作进程: {batch.get('max_workers', 'N/A')}")
        print(f"   - 内存限制: {batch.get('max_memory_mb', 'N/A')}MB")
        
        # 优化配置
        memory = config.get('memory_optimization', {})
        print(f"   - 启用压缩: {memory.get('enable_compression', 'N/A')}")
        print(f"   - 启用流式处理: {memory.get('enable_streaming', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置验证失败: {e}")
        return False


def demo_components():
    """演示核心组件"""
    print("\n🎬 演示3: 核心组件验证")
    print("-" * 50)
    
    try:
        # 演示批处理管理器
        print("   🔧 批处理管理器...")
        from mega_scale.batch_manager import BatchProcessingManager, BatchConfig
        
        batch_config = BatchConfig(batch_size=1000, max_memory_mb=256)
        batch_manager = BatchProcessingManager(batch_config)
        
        # 创建批次
        batches = batch_manager.create_batches(5000)
        print(f"   ✅ 批次创建: {len(batches)} 个批次")
        
        # 计算最优批次大小
        optimal = batch_manager.calculate_optimal_batch_size(10000)
        print(f"   ✅ 最优批次大小: {optimal}")
        
        # 演示内存优化器
        print("   🧠 内存优化器...")
        from mega_scale.memory_optimizer import MemoryOptimizer
        
        memory_optimizer = MemoryOptimizer(256)
        current_memory = memory_optimizer.get_memory_usage_mb()
        print(f"   ✅ 当前内存使用: {current_memory:.1f}MB")
        
        # 演示进度监控器
        print("   📊 进度监控器...")
        from mega_scale.progress_monitor import ProgressMonitor
        
        monitor = ProgressMonitor(1000)
        monitor.start_monitoring(enable_progress_bar=False)
        
        # 模拟进度更新
        for i in range(0, 1001, 200):
            monitor.update_progress(i)
            time.sleep(0.1)
        
        report = monitor.get_status_report()
        print(f"   ✅ 进度监控: {report['progress']['progress_percent']:.1f}% 完成")
        
        monitor.stop_monitoring()
        
        print("   🎉 所有核心组件验证通过!")
        return True
        
    except Exception as e:
        print(f"   ❌ 组件验证失败: {e}")
        return False


def demo_performance_monitoring():
    """演示性能监控"""
    print("\n🎬 演示4: 性能监控系统")
    print("-" * 50)
    
    try:
        from performance_monitor import create_performance_dashboard
        
        # 创建性能监控器
        monitor = create_performance_dashboard()
        monitor.start_monitoring()
        
        print("   📈 性能监控已启动")
        
        # 模拟数据生成过程
        print("   🔄 模拟数据生成过程...")
        for i in range(10):
            # 模拟生成数据
            records_generated = i * 1000
            monitor.update_generation_metrics(records_generated)
            
            # 获取当前统计
            stats = monitor.get_current_stats()
            
            if i % 3 == 0:  # 每3次打印一次
                current = stats.get('current_snapshot', {})
                print(f"   - 已生成: {records_generated:,} 条, "
                      f"CPU: {current.get('cpu_percent', 0):.1f}%, "
                      f"内存: {current.get('memory_percent', 0):.1f}%")
            
            time.sleep(0.5)
        
        # 停止监控
        monitor.stop_monitoring()
        
        # 获取最终统计
        final_stats = monitor.get_current_stats()
        print(f"   ✅ 监控完成, 平均CPU: {final_stats.get('avg_cpu', 0):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 性能监控演示失败: {e}")
        return False


def run_demo():
    """运行完整演示"""
    print("🎪 百万级数据生成系统演示")
    print("=" * 80)
    print("这个演示将展示百万级数据生成系统的核心功能...")
    print()
    
    demos = [
        ("配置系统", demo_configuration),
        ("核心组件", demo_components),
        ("性能监控", demo_performance_monitoring),
        ("小规模数据生成", demo_small_scale)
    ]
    
    passed = 0
    total = len(demos)
    
    for demo_name, demo_func in demos:
        try:
            result = demo_func()
            if result:
                passed += 1
                print(f"✅ {demo_name} - 演示成功")
            else:
                print(f"❌ {demo_name} - 演示失败")
        except Exception as e:
            print(f"❌ {demo_name} - 演示异常: {e}")
    
    print("\n" + "=" * 80)
    print(f"🎭 演示汇总: {passed}/{total} 项成功")
    
    if passed == total:
        print("🎉 所有演示成功! 百万级数据生成系统运行正常。")
        print("\n💡 使用指南:")
        print("   - 查看 MEGA_SCALE_USER_GUIDE.md 了解详细使用方法")
        print("   - 运行 'python mega_main.py --help' 查看命令行选项")
        print("   - 编辑 mega_scale_config.yml 自定义配置")
        print("\n🚀 现在您可以开始生成百万级数据了!")
    else:
        print(f"⚠️ 有 {total-passed} 项演示失败，建议检查系统环境。")
    
    return passed == total


if __name__ == "__main__":
    success = run_demo()
    
    if success:
        print("\n" + "🌟" * 40)
        print("百万级数据生成系统已准备就绪!")
        print("🌟" * 40)
    
    exit(0 if success else 1)