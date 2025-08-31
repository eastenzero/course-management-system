# file: data-generator/test_optimization.py
# 功能: 测试优化后的数据生成脚本

import sys
import time
from pathlib import Path

# 添加路径
sys.path.append(str(Path(__file__).parent))

from optimized_main import OptimizedDataGenerator
from main import generate_complete_dataset
from generators.quality_assessment import DataQualityAssessment


def compare_data_quality():
    """对比原始和优化后的数据质量"""
    print("🔬 开始数据质量对比测试...")
    print("="*60)
    
    quality_assessor = DataQualityAssessment()
    
    # 1. 测试原始数据生成器
    print("\n📊 测试原始数据生成器...")
    start_time = time.time()
    try:
        original_dataset = generate_complete_dataset(
            scale='small',
            output_formats=[],
            validate_data=False
        )
        original_time = time.time() - start_time
        original_quality = quality_assessor.evaluate_data_quality(original_dataset)
        print(f"✅ 原始生成器完成，耗时: {original_time:.2f}秒")
    except Exception as e:
        print(f"❌ 原始生成器测试失败: {e}")
        return
    
    # 2. 测试优化数据生成器
    print("\n🚀 测试优化数据生成器...")
    start_time = time.time()
    try:
        optimized_generator = OptimizedDataGenerator()
        optimized_dataset = optimized_generator.generate_enhanced_dataset(
            scale='small',
            conflict_difficulty='mixed'
        )
        optimized_time = time.time() - start_time
        optimized_quality = optimized_dataset.get('quality_report', {}).get('detailed_scores', {})
        print(f"✅ 优化生成器完成，耗时: {optimized_time:.2f}秒")
    except Exception as e:
        print(f"❌ 优化生成器测试失败: {e}")
        return
    
    # 3. 对比结果
    print("\n📋 质量对比结果:")
    print("-"*60)
    print(f"{'指标':<15} {'原始':<10} {'优化后':<10} {'改进':<10}")
    print("-"*60)
    
    metrics = ['realism', 'complexity', 'diversity', 'consistency', 'algorithm_stress']
    
    for metric in metrics:
        original_score = getattr(original_quality, f'{metric}_score', 0)
        optimized_score = optimized_quality.get(metric, 0)
        improvement = optimized_score - original_score
        
        print(f"{metric:<15} {original_score:<10.3f} {optimized_score:<10.3f} {improvement:+.3f}")
    
    overall_original = original_quality.overall_score
    overall_optimized = optimized_quality.get('overall_score', 0)
    overall_improvement = overall_optimized - overall_original
    
    print("-"*60)
    print(f"{'总体分数':<15} {overall_original:<10.3f} {overall_optimized:<10.3f} {overall_improvement:+.3f}")
    
    # 4. 性能对比
    print(f"\n⏱️  性能对比:")
    print(f"   原始生成器: {original_time:.2f}秒")
    print(f"   优化生成器: {optimized_time:.2f}秒")
    print(f"   时间变化: {optimized_time - original_time:+.2f}秒")
    
    # 5. 数据规模对比
    print(f"\n📊 数据规模对比:")
    original_counts = {
        'students': len(original_dataset.get('students', [])),
        'teachers': len(original_dataset.get('teachers', [])),
        'courses': len(original_dataset.get('courses', [])),
        'enrollments': len(original_dataset.get('enrollments', []))
    }
    
    optimized_counts = {
        'students': len(optimized_dataset.get('students', [])),
        'teachers': len(optimized_dataset.get('teachers', [])),
        'courses': len(optimized_dataset.get('courses', [])),
        'enrollments': len(optimized_dataset.get('enrollments', []))
    }
    
    for data_type in original_counts:
        orig_count = original_counts[data_type]
        opt_count = optimized_counts[data_type]
        print(f"   {data_type}: {orig_count} -> {opt_count}")
    
    # 6. 新增功能展示
    print(f"\n🆕 优化版本新增功能:")
    new_features = [
        f"教师时间偏好: {len(optimized_dataset.get('teacher_preferences', []))} 条",
        f"课程依赖关系: {len(optimized_dataset.get('course_dependencies', {}))} 个课程",
        f"教师能力档案: {len(optimized_dataset.get('teacher_competencies', {}))} 个教师",
        f"冲突场景: {len(optimized_dataset.get('conflicts', []))} 个",
        f"质量评估报告: {'有' if 'quality_report' in optimized_dataset else '无'}"
    ]
    
    for feature in new_features:
        print(f"   ✨ {feature}")
    
    print(f"\n🎯 优化效果总结:")
    if overall_improvement > 0.1:
        print("   🏆 优化效果显著！质量提升超过10%")
    elif overall_improvement > 0.05:
        print("   👍 优化效果良好！质量提升5-10%")
    elif overall_improvement > 0:
        print("   ☑️  优化效果一般，质量略有提升")
    else:
        print("   ⚠️  优化效果不明显，需要进一步调整")


if __name__ == "__main__":
    compare_data_quality()