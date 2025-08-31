# file: data-generator/mega_main.py
# 功能: 百万级数据生成主程序

import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from mega_scale import MegaDataGenerator
from mega_scale.mega_generator import MegaGenerationConfig
from performance_monitor import create_performance_dashboard


def load_config(config_file: str = "mega_scale_config.yml") -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"❌ 配置文件不存在: {config_file}")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ 配置文件格式错误: {e}")
        return {}


def create_generation_config(yaml_config: Dict[str, Any]) -> MegaGenerationConfig:
    """从YAML配置创建生成配置"""
    generation_cfg = yaml_config.get('generation', {})
    batch_cfg = yaml_config.get('batch_processing', {})
    memory_cfg = yaml_config.get('memory_optimization', {})
    output_cfg = yaml_config.get('output', {})
    
    return MegaGenerationConfig(
        target_records=generation_cfg.get('target_records', 1000000),
        batch_size=batch_cfg.get('batch_size', 50000),
        max_memory_mb=batch_cfg.get('max_memory_mb', 2048),
        max_workers=batch_cfg.get('max_workers', 8),
        enable_compression=memory_cfg.get('enable_compression', True),
        enable_streaming=memory_cfg.get('enable_streaming', True),
        enable_checkpoints=yaml_config.get('checkpoints', {}).get('enable_checkpoints', True),
        output_formats=output_cfg.get('formats', ['json'])
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='百万级数据生成系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python mega_main.py                    # 使用默认配置
  python mega_main.py --config custom.yml # 使用自定义配置
  python mega_main.py --scale large      # 指定数据规模
  python mega_main.py --output ./data    # 指定输出目录
  python mega_main.py --monitor         # 启用性能监控
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='mega_scale_config.yml',
        help='配置文件路径 (默认: mega_scale_config.yml)'
    )
    
    parser.add_argument(
        '--scale', '-s',
        choices=['huge', 'large', 'medium', 'small'],
        help='数据规模 (覆盖配置文件设置)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='输出目录 (覆盖配置文件设置)'
    )
    
    parser.add_argument(
        '--target-records', '-n',
        type=int,
        help='目标记录数 (覆盖配置文件设置)'
    )
    
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        help='批次大小 (覆盖配置文件设置)'
    )
    
    parser.add_argument(
        '--workers', '-w',
        type=int,
        help='工作进程数 (覆盖配置文件设置)'
    )
    
    parser.add_argument(
        '--memory', '-m',
        type=int,
        help='最大内存限制MB (覆盖配置文件设置)'
    )
    
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='启用性能监控'
    )
    
    parser.add_argument(
        '--no-compression',
        action='store_true',
        help='禁用压缩'
    )
    
    parser.add_argument(
        '--no-streaming',
        action='store_true',
        help='禁用流式处理'
    )
    
    parser.add_argument(
        '--conflict-difficulty',
        choices=['simple', 'medium', 'complex', 'mixed'],
        default='mixed',
        help='冲突难度级别 (默认: mixed)'
    )
    
    args = parser.parse_args()
    
    # 加载配置
    print(f"📋 加载配置文件: {args.config}")
    yaml_config = load_config(args.config)
    
    if not yaml_config:
        print("❌ 无法加载配置，使用默认配置")
        yaml_config = {}
    
    # 创建生成配置
    config = create_generation_config(yaml_config)
    
    # 命令行参数覆盖
    if args.target_records:
        config.target_records = args.target_records
    if args.batch_size:
        config.batch_size = args.batch_size
    if args.workers:
        config.max_workers = args.workers
    if args.memory:
        config.max_memory_mb = args.memory
    if args.no_compression:
        config.enable_compression = False
    if args.no_streaming:
        config.enable_streaming = False
    
    # 确定数据规模和输出目录
    scale = args.scale or yaml_config.get('generation', {}).get('scale', 'huge')
    output_dir = args.output or yaml_config.get('generation', {}).get('output_dir', 'mega_output')
    conflict_difficulty = args.conflict_difficulty
    
    # 打印配置信息
    print(f"\n{'='*80}")
    print(f"🚀 百万级数据生成系统启动")
    print(f"{'='*80}")
    print(f"📊 数据规模: {scale}")
    print(f"🎯 目标记录数: {config.target_records:,}")
    print(f"📦 批次大小: {config.batch_size:,}")
    print(f"💾 内存限制: {config.max_memory_mb}MB")
    print(f"⚡ 工作进程: {config.max_workers}")
    print(f"📁 输出目录: {output_dir}")
    print(f"🔧 压缩: {'启用' if config.enable_compression else '禁用'}")
    print(f"🌊 流式处理: {'启用' if config.enable_streaming else '禁用'}")
    print(f"⚡ 冲突难度: {conflict_difficulty}")
    print(f"{'='*80}")
    
    # 初始化性能监控
    performance_monitor = None
    if args.monitor:
        print("📊 启动性能监控...")
        performance_monitor = create_performance_dashboard()
        performance_monitor.start_monitoring()
    
    try:
        # 创建生成器
        generator = MegaDataGenerator(config)
        
        # 开始生成
        print(f"\n🎬 开始百万级数据生成...")
        start_time = sys.modules['time'].time()
        
        results = generator.generate_mega_dataset(
            scale=scale,
            output_dir=output_dir,
            conflict_difficulty=conflict_difficulty
        )
        
        end_time = sys.modules['time'].time()
        total_time = end_time - start_time
        
        # 打印最终统计
        if results and results.get('success'):
            stats = results.get('performance_stats', {})
            total_records = stats.get('total_records', 0)
            
            print(f"\n{'='*80}")
            print(f"🎉 百万级数据生成成功完成！")
            print(f"{'='*80}")
            print(f"⏱️  总耗时: {total_time:.1f} 秒")
            print(f"📊 总记录数: {total_records:,}")
            print(f"🚀 平均速度: {total_records/total_time:.0f} 条/秒")
            
            memory_stats = stats.get('memory_stats', {})
            if memory_stats:
                print(f"💾 峰值内存: {memory_stats.get('peak_memory_mb', 0):.0f}MB")
                print(f"🧹 GC次数: {memory_stats.get('gc_count', 0)}")
            
            parallel_stats = stats.get('parallel_stats', {})
            if parallel_stats:
                print(f"⚡ 并行效率: {parallel_stats.get('parallel_efficiency', 0):.1f}%")
            
            print(f"📁 输出位置: {output_dir}")
            print(f"{'='*80}")
            
            return 0
        else:
            print("❌ 数据生成失败")
            return 1
    
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断，正在清理资源...")
        return 130
    
    except Exception as e:
        print(f"\n❌ 生成过程发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # 停止性能监控
        if performance_monitor:
            print("📊 停止性能监控...")
            performance_monitor.stop_monitoring()
            
            # 生成性能报告
            try:
                performance_monitor.generate_performance_report("performance_reports")
                print("📊 性能报告已生成")
            except Exception as e:
                print(f"❌ 生成性能报告失败: {e}")


if __name__ == "__main__":
    exit(main())