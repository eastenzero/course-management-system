# file: data-generator/test_mega_generation.py
# 功能: 百万级数据生成系统测试

import sys
import time
import shutil
from pathlib import Path
from typing import Dict, Any

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from mega_scale.mega_generator import MegaDataGenerator, MegaGenerationConfig
from performance_monitor import create_performance_dashboard


def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试1: 基本功能验证")
    print("-" * 50)
    
    try:
        # 小规模测试配置
        config = MegaGenerationConfig(
            target_records=10000,  # 1万条记录
            batch_size=2000,
            max_memory_mb=512,
            max_workers=2,
            enable_compression=False,
            enable_streaming=True
        )
        
        generator = MegaDataGenerator(config)
        
        print("   ✅ 生成器创建成功")
        
        # 测试系统初始化
        generator._initialize_system()
        print("   ✅ 系统初始化成功")
        
        # 清理
        generator._cleanup_resources()
        print("   ✅ 资源清理成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 基本功能测试失败: {e}")
        return False


def test_batch_processing():
    """测试批处理功能"""
    print("\n🧪 测试2: 批处理功能验证")
    print("-" * 50)
    
    try:
        from mega_scale.batch_manager import BatchProcessingManager, BatchConfig
        
        config = BatchConfig(
            batch_size=1000,
            max_memory_mb=256,
            max_workers=2
        )
        
        manager = BatchProcessingManager(config)
        
        # 测试批次创建
        batches = manager.create_batches(5000)
        print(f"   ✅ 创建批次: {len(batches)} 个")
        
        # 测试最优批次大小计算
        optimal_size = manager.calculate_optimal_batch_size(10000)
        print(f"   ✅ 最优批次大小: {optimal_size}")
        
        # 测试进度摘要
        summary = manager.get_progress_summary()
        print(f"   ✅ 进度摘要获取成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 批处理功能测试失败: {e}")
        return False


def test_memory_optimization():
    """测试内存优化功能"""
    print("\n🧪 测试3: 内存优化功能验证")
    print("-" * 50)
    
    try:
        from mega_scale.memory_optimizer import MemoryOptimizer
        
        optimizer = MemoryOptimizer(max_memory_mb=512)
        
        # 测试内存监控
        memory_usage = optimizer.get_memory_usage_mb()
        print(f"   ✅ 当前内存使用: {memory_usage:.1f}MB")
        
        # 测试垃圾回收
        freed = optimizer.force_gc()
        print(f"   ✅ 垃圾回收释放: {freed:.1f}MB")
        
        # 测试大规模优化建议
        recommendations = optimizer.optimize_for_large_scale(100000)
        print(f"   ✅ 优化建议: {len(recommendations['optimizations_applied'])} 项")
        
        # 测试流式写入
        test_file = "test_stream_output.json"
        optimizer.write_incrementally(test_file, {"test": "data"})
        print("   ✅ 流式写入测试成功")
        
        # 清理测试文件
        Path(test_file).unlink(missing_ok=True)
        
        optimizer.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ 内存优化功能测试失败: {e}")
        return False


def test_parallel_engine():
    """测试并行计算引擎"""
    print("\n🧪 测试4: 并行计算引擎验证")
    print("-" * 50)
    
    try:
        from mega_scale.parallel_engine import ParallelComputingEngine, TaskConfig
        
        engine = ParallelComputingEngine(max_workers=2)
        engine.initialize_workers(process_workers=1, thread_workers=1)
        engine.start_processing()
        
        # 注册测试任务函数
        def test_task(start, end, multiplier=1):
            return [(i * multiplier) for i in range(start, end)]
        
        engine.register_task_function('test_task', test_task)
        
        # 提交测试任务
        task_config = TaskConfig(
            task_id="test_task_1",
            task_type="test_task",
            priority=5,
            estimated_duration=1.0
        )
        
        task_id = engine.submit_task(task_config, test_task, 1, 10, multiplier=2)
        print(f"   ✅ 任务提交成功: {task_id}")
        
        # 等待完成
        completed = engine.wait_for_completion(timeout=10.0)
        print(f"   ✅ 任务完成状态: {completed}")
        
        # 获取结果
        results = engine.get_results()
        if task_id in results:
            print(f"   ✅ 任务结果获取成功")
        
        # 获取性能统计
        stats = engine.get_performance_stats()
        print(f"   ✅ 性能统计: 处理任务 {stats['total_tasks_processed']} 个")
        
        engine.stop()
        return True
        
    except Exception as e:
        print(f"   ❌ 并行计算引擎测试失败: {e}")
        return False


def test_progress_monitoring():
    """测试进度监控功能"""
    print("\n🧪 测试5: 进度监控功能验证")
    print("-" * 50)
    
    try:
        from mega_scale.progress_monitor import ProgressMonitor
        
        monitor = ProgressMonitor(total_records=1000)
        monitor.start_monitoring(enable_progress_bar=False)
        
        # 模拟进度更新
        for i in range(0, 1001, 100):
            monitor.update_progress(i)
            time.sleep(0.1)
        
        # 测试错误处理
        try:
            raise ValueError("测试错误")
        except Exception as e:
            error_id = monitor.handle_error(e, {'test': True})
            print(f"   ✅ 错误处理成功: {error_id}")
        
        # 获取状态报告
        report = monitor.get_status_report()
        print(f"   ✅ 状态报告获取成功")
        
        monitor.stop_monitoring()
        return True
        
    except Exception as e:
        print(f"   ❌ 进度监控功能测试失败: {e}")
        return False


def test_performance_monitoring():
    """测试性能监控功能"""
    print("\n🧪 测试6: 性能监控功能验证")
    print("-" * 50)
    
    try:
        monitor = create_performance_dashboard()
        monitor.start_monitoring()
        
        # 模拟数据生成
        for i in range(5):
            monitor.update_generation_metrics(i * 1000)
            time.sleep(0.5)
        
        # 获取统计信息
        stats = monitor.get_current_stats()
        print(f"   ✅ 性能统计获取成功")
        
        # 获取趋势数据
        trends = monitor.get_performance_trends()
        print(f"   ✅ 趋势数据获取成功: {len(trends['timestamps'])} 个快照")
        
        monitor.stop_monitoring()
        return True
        
    except Exception as e:
        print(f"   ❌ 性能监控功能测试失败: {e}")
        return False


def test_configuration_loading():
    """测试配置文件加载"""
    print("\n🧪 测试7: 配置文件加载验证")
    print("-" * 50)
    
    try:
        import yaml
        
        # 检查配置文件是否存在
        config_file = "mega_scale_config.yml"
        if not Path(config_file).exists():
            print(f"   ⚠️ 配置文件不存在: {config_file}")
            return False
        
        # 加载配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"   ✅ 配置文件加载成功")
        
        # 验证关键配置项
        required_sections = ['generation', 'batch_processing', 'memory_optimization', 'output']
        for section in required_sections:
            if section in config:
                print(f"   ✅ 配置段 '{section}' 存在")
            else:
                print(f"   ❌ 配置段 '{section}' 缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置文件加载测试失败: {e}")
        return False


def test_small_scale_generation():
    """测试小规模数据生成"""
    print("\n🧪 测试8: 小规模数据生成验证")
    print("-" * 50)
    
    try:
        # 小规模配置
        config = MegaGenerationConfig(
            target_records=5000,  # 5千条记录
            batch_size=1000,
            max_memory_mb=512,
            max_workers=2,
            enable_compression=False,
            enable_streaming=True,
            output_formats=['json']
        )
        
        generator = MegaDataGenerator(config)
        
        # 创建测试输出目录
        test_output_dir = "test_mega_output"
        if Path(test_output_dir).exists():
            shutil.rmtree(test_output_dir)
        
        print("   🚀 开始小规模数据生成...")
        start_time = time.time()
        
        results = generator.generate_mega_dataset(
            scale='small',
            output_dir=test_output_dir,
            conflict_difficulty='simple'
        )
        
        end_time = time.time()
        
        if results and results.get('success'):
            stats = results.get('performance_stats', {})
            total_records = stats.get('total_records', 0)
            
            print(f"   ✅ 数据生成成功!")
            print(f"   📊 总记录数: {total_records:,}")
            print(f"   ⏱️ 耗时: {end_time - start_time:.1f} 秒")
            print(f"   🚀 平均速度: {total_records/(end_time - start_time):.0f} 条/秒")
            
            # 验证输出文件
            output_path = Path(test_output_dir)
            if output_path.exists():
                output_files = list(output_path.glob("*.json"))
                print(f"   📁 生成文件: {len(output_files)} 个")
            
            return True
        else:
            print("   ❌ 数据生成失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 小规模数据生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试文件
        test_output_dir = "test_mega_output"
        if Path(test_output_dir).exists():
            try:
                shutil.rmtree(test_output_dir)
                print("   🧹 测试文件清理完成")
            except:
                pass


def run_all_tests():
    """运行所有测试"""
    print("🧪 百万级数据生成系统功能测试")
    print("=" * 80)
    
    tests = [
        ("基本功能", test_basic_functionality),
        ("批处理功能", test_batch_processing),
        ("内存优化", test_memory_optimization),
        ("并行计算引擎", test_parallel_engine),
        ("进度监控", test_progress_monitoring),
        ("性能监控", test_performance_monitoring),
        ("配置文件加载", test_configuration_loading),
        ("小规模数据生成", test_small_scale_generation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_name} - 通过")
            else:
                failed += 1
                print(f"❌ {test_name} - 失败")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} - 异常: {e}")
    
    print("\n" + "=" * 80)
    print(f"🧪 测试汇总: 通过 {passed} 项, 失败 {failed} 项")
    
    if failed == 0:
        print("🎉 所有测试通过! 百万级数据生成系统运行正常。")
        return True
    else:
        print(f"⚠️ 有 {failed} 项测试失败，建议检查相关功能。")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)