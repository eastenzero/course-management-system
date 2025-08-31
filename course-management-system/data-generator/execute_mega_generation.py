#!/usr/bin/env python3
"""
执行百万级数据生成的脚本
"""

import sys
import time
import yaml
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from mega_scale import MegaDataGenerator
from mega_scale.mega_generator import MegaGenerationConfig

def main():
    print("🚀 开始百万级数据生成任务")
    print("="*80)
    
    # 加载配置
    config_file = Path(__file__).parent / "mega_scale_config.yml"
    with open(config_file, 'r', encoding='utf-8') as f:
        yaml_config = yaml.safe_load(f)
    
    # 创建生成配置 - 先生成50万条记录进行测试
    config = MegaGenerationConfig(
        target_records=500000,  # 50万条记录
        batch_size=25000,       # 2.5万批次大小
        max_memory_mb=1536,     # 1.5GB内存限制
        max_workers=6,          # 6个工作进程
        enable_compression=True,
        enable_streaming=True,
        enable_checkpoints=True,
        output_formats=['json', 'sql']
    )
    
    print(f"📊 生成配置:")
    print(f"   🎯 目标记录数: {config.target_records:,}")
    print(f"   📦 批次大小: {config.batch_size:,}")
    print(f"   💾 内存限制: {config.max_memory_mb}MB")
    print(f"   ⚡ 工作进程: {config.max_workers}")
    print(f"   🗜️  压缩: {config.enable_compression}")
    print(f"   🌊 流式处理: {config.enable_streaming}")
    print(f"   📋 输出格式: {config.output_formats}")
    print("="*80)
    
    try:
        # 创建生成器
        print("🔧 初始化MegaDataGenerator...")
        generator = MegaDataGenerator(config)
        
        # 开始生成
        print(f"🎬 开始生成数据... {datetime.now()}")
        start_time = time.time()
        
        results = generator.generate_mega_dataset(
            scale="large",
            output_dir="mega_output_corrected",
            conflict_difficulty="mixed"
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 输出结果
        print("\n" + "="*80)
        print("🎉 数据生成完成！")
        print(f"⏱️  总耗时: {duration:.2f} 秒 ({duration/60:.1f} 分钟)")
        
        if results and 'metadata' in results:
            metadata = results['metadata']
            total_records = metadata.get('total_records', 0)
            generation_speed = total_records / duration if duration > 0 else 0
            
            print(f"📊 生成统计:")
            print(f"   📈 总记录数: {total_records:,}")
            print(f"   🚀 生成速度: {generation_speed:.0f} 条/秒")
            print(f"   ✅ 验证状态: {metadata.get('validation_passed', '未知')}")
            
            if metadata.get('output_files'):
                print(f"   📁 输出文件:")
                for file_path in metadata['output_files']:
                    print(f"      - {file_path}")
        
        print("="*80)
        return results
        
    except Exception as e:
        print(f"❌ 数据生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = main()
    if results:
        print("✅ 数据生成任务完成")
    else:
        print("❌ 数据生成任务失败")
        sys.exit(1)