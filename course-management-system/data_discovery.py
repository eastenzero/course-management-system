#!/usr/bin/env python3
"""
数据发现脚本 - 分析已生成的测试数据
功能：扫描data-generator目录，发现数据文件并提供数据集选择建议
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class DataDiscovery:
    """数据发现类"""
    
    def __init__(self, base_dir: str = None):
        """初始化数据发现器"""
        if base_dir is None:
            self.base_dir = Path(__file__).parent / "data-generator"
        else:
            self.base_dir = Path(base_dir)
        
        self.data_directories = [
            self.base_dir / "data_output",
            self.base_dir / "data_output_medium", 
            self.base_dir / "data_output_large",
            self.base_dir / "output"
        ]
    
    def scan_data_files(self) -> Dict[str, Any]:
        """扫描所有数据文件"""
        discovered_files = {}
        
        print("🔍 扫描数据生成器目录...")
        print(f"📁 基础目录: {self.base_dir}")
        print("-" * 60)
        
        for data_dir in self.data_directories:
            if not data_dir.exists():
                print(f"⚠️  目录不存在: {data_dir}")
                continue
                
            print(f"📂 扫描目录: {data_dir}")
            
            # 扫描JSON文件
            json_files = list(data_dir.rglob("*.json"))
            sql_files = list(data_dir.rglob("*.sql"))
            
            if json_files or sql_files:
                discovered_files[data_dir.name] = {
                    'path': str(data_dir),
                    'json_files': [str(f) for f in json_files],
                    'sql_files': [str(f) for f in sql_files],
                    'file_count': len(json_files) + len(sql_files),
                    'size_mb': self._calculate_dir_size(data_dir)
                }
                
                print(f"   ✅ 发现 {len(json_files)} 个JSON文件, {len(sql_files)} 个SQL文件")
                print(f"   📊 目录大小: {discovered_files[data_dir.name]['size_mb']:.1f} MB")
            else:
                print(f"   ❌ 未发现数据文件")
        
        return discovered_files
    
    def _calculate_dir_size(self, directory: Path) -> float:
        """计算目录大小(MB)"""
        total_size = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size / (1024 * 1024)  # 转换为MB
        except Exception as e:
            print(f"   ⚠️  计算目录大小失败: {e}")
            return 0.0
    
    def analyze_data_structure(self, json_file_path: str) -> Dict[str, Any]:
        """分析JSON数据文件结构"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                # 只读取开头部分避免内存问题
                sample_data = f.read(10000)  # 读取前10KB
                f.seek(0)
                
                # 尝试解析完整JSON（小文件）或部分JSON（大文件）
                try:
                    data = json.load(f)
                except (json.JSONDecodeError, MemoryError):
                    # 如果文件太大，只分析样本
                    try:
                        # 尝试解析部分数据
                        data = json.loads(sample_data + "}")
                    except:
                        return {"error": "无法解析JSON文件"}
            
            analysis = {
                'file_path': json_file_path,
                'file_size_mb': Path(json_file_path).stat().st_size / (1024 * 1024),
                'structure': {},
                'record_counts': {},
                'metadata': data.get('metadata', {})
            }
            
            # 分析数据结构
            for key, value in data.items():
                if isinstance(value, list):
                    analysis['record_counts'][key] = len(value)
                    if value:  # 如果列表非空，分析第一个元素的结构
                        analysis['structure'][key] = list(value[0].keys()) if isinstance(value[0], dict) else type(value[0]).__name__
                elif isinstance(value, dict):
                    analysis['structure'][key] = list(value.keys())
                else:
                    analysis['structure'][key] = type(value).__name__
            
            return analysis
            
        except Exception as e:
            return {"error": f"分析失败: {str(e)}"}
    
    def recommend_dataset(self, discovered_files: Dict[str, Any]) -> Optional[str]:
        """推荐最佳数据集"""
        print("\n🎯 数据集分析与推荐...")
        print("-" * 60)
        
        recommendations = []
        
        for dir_name, file_info in discovered_files.items():
            if not file_info['json_files']:
                continue
            
            # 选择第一个JSON文件进行分析
            json_file = file_info['json_files'][0]
            analysis = self.analyze_data_structure(json_file)
            
            if 'error' in analysis:
                print(f"❌ {dir_name}: {analysis['error']}")
                continue
            
            total_records = sum(analysis['record_counts'].values())
            score = self._calculate_recommendation_score(file_info, analysis)
            
            recommendations.append({
                'dir_name': dir_name,
                'file_path': json_file,
                'total_records': total_records,
                'file_size_mb': analysis['file_size_mb'],
                'score': score,
                'metadata': analysis.get('metadata', {}),
                'record_counts': analysis['record_counts']
            })
            
            print(f"📊 {dir_name}:")
            print(f"   📁 文件: {Path(json_file).name}")
            print(f"   📏 大小: {analysis['file_size_mb']:.1f} MB")
            print(f"   📈 记录数: {total_records:,}")
            print(f"   🏆 推荐分数: {score:.1f}/10")
            
            # 显示各类型记录数量
            if analysis['record_counts']:
                print("   📋 数据详情:")
                for data_type, count in analysis['record_counts'].items():
                    if data_type != 'metadata':
                        print(f"      - {data_type}: {count:,} 条")
        
        if not recommendations:
            print("❌ 未发现可用的数据集")
            return None
        
        # 按分数排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        best_recommendation = recommendations[0]
        
        print(f"\n🏆 推荐数据集: {best_recommendation['dir_name']}")
        print(f"   📁 文件路径: {best_recommendation['file_path']}")
        print(f"   🎯 推荐理由: 数据量适中，质量较好，适合演示和测试")
        
        return best_recommendation['file_path']
    
    def _calculate_recommendation_score(self, file_info: Dict, analysis: Dict) -> float:
        """计算推荐分数 (0-10分)"""
        score = 5.0  # 基础分数
        
        # 文件大小评分 (适中的文件大小得分更高)
        size_mb = analysis['file_size_mb']
        if 10 <= size_mb <= 100:  # 10-100MB 最佳
            score += 2.0
        elif 1 <= size_mb <= 200:  # 1-200MB 良好
            score += 1.0
        elif size_mb > 500:  # 超过500MB 扣分
            score -= 1.0
        
        # 记录数量评分
        total_records = sum(analysis['record_counts'].values())
        if 1000 <= total_records <= 100000:  # 1K-100K记录最佳
            score += 2.0
        elif 100 <= total_records <= 200000:  # 100-200K记录良好
            score += 1.0
        
        # 数据完整性评分
        required_tables = ['departments', 'students', 'teachers', 'courses', 'enrollments']
        existing_tables = set(analysis['record_counts'].keys())
        completeness = len(existing_tables.intersection(required_tables)) / len(required_tables)
        score += completeness * 2.0
        
        # 元数据评分
        if analysis.get('metadata') and 'validation_passed' in analysis['metadata']:
            if analysis['metadata'].get('validation_passed', False):
                score += 1.0
        
        return min(score, 10.0)  # 最高10分
    
    def generate_report(self, discovered_files: Dict[str, Any], recommended_file: str = None) -> None:
        """生成发现报告"""
        print(f"\n📋 数据发现报告")
        print("=" * 60)
        print(f"🕐 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 扫描目录数: {len(self.data_directories)}")
        print(f"📁 发现数据集: {len(discovered_files)}")
        
        if recommended_file:
            print(f"🎯 推荐数据集: {Path(recommended_file).parent.name}")
            print(f"📄 推荐文件: {Path(recommended_file).name}")
        
        print("\n📊 数据集概览:")
        total_size = 0
        total_files = 0
        
        for dir_name, info in discovered_files.items():
            print(f"  📁 {dir_name}:")
            print(f"     📄 文件数: {info['file_count']}")
            print(f"     📏 大小: {info['size_mb']:.1f} MB")
            total_size += info['size_mb']
            total_files += info['file_count']
        
        print(f"\n📈 总计:")
        print(f"  📄 文件总数: {total_files}")
        print(f"  📏 总大小: {total_size:.1f} MB")
        
        if recommended_file:
            print(f"\n✅ 建议使用数据集: {recommended_file}")
        else:
            print(f"\n❌ 未找到合适的数据集")


def main():
    """主函数"""
    print("🚀 课程管理系统 - 数据发现工具")
    print("=" * 60)
    
    # 初始化数据发现器
    discovery = DataDiscovery()
    
    # 扫描数据文件
    discovered_files = discovery.scan_data_files()
    
    if not discovered_files:
        print("\n❌ 未发现任何数据文件！")
        print("请确保数据生成器已运行并生成了测试数据。")
        return False
    
    # 推荐数据集
    recommended_file = discovery.recommend_dataset(discovered_files)
    
    # 生成报告
    discovery.generate_report(discovered_files, recommended_file)
    
    return recommended_file


if __name__ == "__main__":
    recommended_file = main()
    if recommended_file:
        print(f"\n🎉 数据发现完成！推荐数据文件：")
        print(f"📄 {recommended_file}")
        
        # 将推荐文件路径保存到环境变量文件
        env_file = Path(__file__).parent / ".recommended_data_file"
        with open(env_file, 'w') as f:
            f.write(recommended_file)
        print(f"💾 推荐路径已保存到: {env_file}")
    else:
        sys.exit(1)