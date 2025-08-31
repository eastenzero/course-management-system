#!/usr/bin/env python3
"""
简单测试mega系统是否可以正常工作
"""

import sys
import yaml
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

try:
    from mega_scale import MegaDataGenerator
    from mega_scale.mega_generator import MegaGenerationConfig
    print("✅ 成功导入MegaDataGenerator模块")
except ImportError as e:
    print(f"❌ 导入MegaDataGenerator失败: {e}")
    sys.exit(1)

try:
    # 加载配置
    config_file = Path(__file__).parent / "mega_scale_config.yml"
    with open(config_file, 'r', encoding='utf-8') as f:
        yaml_config = yaml.safe_load(f)
    print("✅ 成功加载配置文件")
except Exception as e:
    print(f"❌ 加载配置文件失败: {e}")
    sys.exit(1)

try:
    # 创建配置对象
    generation_cfg = yaml_config.get('generation', {})
    batch_cfg = yaml_config.get('batch_processing', {})
    memory_cfg = yaml_config.get('memory_optimization', {})
    output_cfg = yaml_config.get('output', {})
    
    config = MegaGenerationConfig(
        target_records=10000,  # 测试用小数据量
        batch_size=1000,
        max_memory_mb=512,
        max_workers=2,
        enable_compression=True,
        enable_streaming=True,
        enable_checkpoints=False,  # 测试时不需要检查点
        output_formats=['json']
    )
    print("✅ 成功创建生成配置")
except Exception as e:
    print(f"❌ 创建配置失败: {e}")
    sys.exit(1)

try:
    # 创建生成器
    generator = MegaDataGenerator(config)
    print("✅ 成功创建MegaDataGenerator实例")
except Exception as e:
    print(f"❌ 创建生成器失败: {e}")
    sys.exit(1)

print("\n🎉 Mega系统测试通过！系统已准备好进行百万级数据生成")
print(f"📋 测试配置:")
print(f"   - 目标记录数: {config.target_records:,}")
print(f"   - 批次大小: {config.batch_size:,}")
print(f"   - 内存限制: {config.max_memory_mb}MB")
print(f"   - 工作进程: {config.max_workers}")