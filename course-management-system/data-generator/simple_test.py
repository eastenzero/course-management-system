# file: data-generator/simple_test.py
# 功能: 简化的优化测试脚本

import sys
from pathlib import Path

# 添加路径
sys.path.append(str(Path(__file__).parent))

from generators.realistic_constraints import RealisticConstraintsEngine
from generators.relationship_modeling import RelationshipModelingEngine
from generators.conflict_generator import ConflictGeneratorEngine
from generators.quality_assessment import DataQualityAssessment


def demonstrate_optimization_features():
    """演示优化功能"""
    print("🚀 数据生成脚本优化演示")
    print("="*60)
    
    # 1. 真实性约束引擎
    print("\n📊 1. 真实性约束引擎")
    print("-"*40)
    realistic_engine = RealisticConstraintsEngine()
    
    # 模拟教师数据
    sample_teacher = {
        'id': 1,
        'name': '张教授',
        'title': '教授',
        'birth_year': 1970,
        'department': '计算机科学与技术学院'
    }
    
    try:
        # 生成真实的教师时间偏好
        prefs = realistic_engine.generate_realistic_teacher_preferences(sample_teacher)
        print(f"✅ 为教师生成了真实的时间偏好配置")
        print(f"   - 配置类型: {prefs['profile_type']}")
        print(f"   - 每日最大课时: {prefs['constraints']['max_daily_hours']}")
        print(f"   - 最小休息时间: {prefs['constraints']['min_break_minutes']}分钟")
    except Exception as e:
        print(f"❌ 真实性约束测试失败: {e}")
    
    # 2. 关联性建模引擎
    print("\n🔗 2. 关联性建模引擎")  
    print("-"*40)
    relationship_engine = RelationshipModelingEngine()
    
    # 模拟课程数据
    sample_courses = [
        {'id': 1, 'name': '高等数学', 'department_id': 1, 'difficulty_level': 1},
        {'id': 2, 'name': '线性代数', 'department_id': 1, 'difficulty_level': 2},
        {'id': 3, 'name': '数据结构与算法', 'department_id': 1, 'difficulty_level': 3}
    ]
    
    try:
        dependencies = relationship_engine.build_course_dependency_network(sample_courses)
        print(f"✅ 构建了课程依赖网络")
        print(f"   - 分析了 {len(sample_courses)} 门课程")
        print(f"   - 发现了 {len(dependencies)} 个依赖关系")
        
        for course_id, deps in dependencies.items():
            if deps:
                print(f"   - 课程{course_id}有{len(deps)}个先修要求")
    except Exception as e:
        print(f"❌ 关联性建模测试失败: {e}")
    
    # 3. 冲突生成引擎
    print("\n⚡ 3. 分级冲突生成引擎")
    print("-"*40)
    conflict_engine = ConflictGeneratorEngine()
    
    # 模拟基础数据
    sample_teachers = [{'id': i, 'name': f'教师{i}'} for i in range(1, 11)]
    sample_classrooms = [{'id': i, 'name': f'教室{i}', 'capacity': 50} for i in range(1, 6)]
    
    try:
        conflicts = conflict_engine.generate_conflict_scenarios(
            sample_courses, sample_teachers, sample_classrooms, 'mixed'
        )
        
        print(f"✅ 生成了 {len(conflicts)} 个冲突场景")
        
        # 统计冲突类型
        conflict_stats = conflict_engine.generate_conflict_statistics()
        print(f"   - 严重程度分布: {conflict_stats.get('severity_distribution', {})}")
        print(f"   - 类型分布: {list(conflict_stats.get('type_distribution', {}).keys())}")
        print(f"   - 算法压力测试点: {len(conflict_stats.get('algorithm_stress_coverage', []))}个")
        
    except Exception as e:
        print(f"❌ 冲突生成测试失败: {e}")
    
    # 4. 数据质量评估
    print("\n📈 4. 数据质量评估体系")
    print("-"*40)
    quality_assessor = DataQualityAssessment()
    
    # 模拟数据集
    sample_dataset = {
        'courses': sample_courses,
        'teachers': sample_teachers,
        'students': [{'id': i, 'name': f'学生{i}'} for i in range(1, 101)],
        'enrollments': [{'student_id': i, 'course_id': j} for i in range(1, 11) for j in range(1, 4)],
        'conflicts': conflicts if 'conflicts' in locals() else []
    }
    
    try:
        quality_metrics = quality_assessor.evaluate_data_quality(sample_dataset)
        
        print(f"✅ 完成数据质量评估")
        print(f"   - 真实性分数: {quality_metrics.realism_score:.3f}")
        print(f"   - 复杂性分数: {quality_metrics.complexity_score:.3f}")
        print(f"   - 多样性分数: {quality_metrics.diversity_score:.3f}")
        print(f"   - 一致性分数: {quality_metrics.consistency_score:.3f}")
        print(f"   - 算法压力分数: {quality_metrics.algorithm_stress_score:.3f}")
        print(f"   - 综合分数: {quality_metrics.overall_score:.3f}")
        
        grade = quality_assessor._get_quality_grade(quality_metrics.overall_score)
        print(f"   - 质量等级: {grade}")
        
    except Exception as e:
        print(f"❌ 质量评估测试失败: {e}")
    
    # 5. 优化效果总结
    print("\n🎯 优化效果总结")
    print("-"*40)
    print("✨ 新增核心功能:")
    print("   1. 基于年龄、职称的真实教师时间偏好建模")
    print("   2. 基于知识图谱的课程依赖关系自动构建")
    print("   3. 分级冲突场景生成(基础/复杂/极限)")
    print("   4. 多维度数据质量评估体系")
    print("   5. 帕累托分布的课程热度建模")
    print("   6. 教师-课程智能匹配算法")
    
    print("\n🚀 预期算法优势体现:")
    print("   • 更真实的时间约束测试排课算法的时间管理能力")
    print("   • 复杂的依赖关系验证算法的约束处理能力")  
    print("   • 分级冲突场景全面测试算法的鲁棒性")
    print("   • 资源竞争模拟验证算法的优化效果")
    print("   • 质量评估体系提供客观的性能对比基准")
    
    print(f"\n{'='*60}")
    print("🏆 数据生成脚本优化完成！")
    print("📊 新版本数据生成器将显著提升排课算法测试的有效性")


if __name__ == "__main__":
    demonstrate_optimization_features()