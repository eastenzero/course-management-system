# file: data-generator/quick_test.py
# 功能: 快速测试核心功能

import sys
from pathlib import Path

# 添加生成器模块路径
sys.path.append(str(Path(__file__).parent / 'generators'))

def test_import():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        from course_scheduling_constraints import (
            CourseSchedulingConstraints, TimeSlot, CourseType, 
            DifficultyLevel, TeacherTitle
        )
        print("✅ 约束模块导入成功")
        
        from constraint_aware_generator import (
            ConstraintAwareCourseGenerator, GenerationConfig, GenerationMode
        )
        print("✅ 生成器模块导入成功")
        
        from data_quality_validator import DataQualityAssessment
        print("✅ 质量验证模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_basic_generation():
    """测试基本数据生成"""
    print("\n🧪 测试基本数据生成...")
    
    try:
        from constraint_aware_generator import ConstraintAwareCourseGenerator, GenerationConfig
        
        # 创建最小配置
        config = GenerationConfig(
            target_students=10,
            target_teachers=5,
            target_courses=20,
            target_schedules=50,
            departments=['计算机学院']
        )
        
        # 生成数据
        generator = ConstraintAwareCourseGenerator(config)
        result = generator.generate_complete_dataset()
        
        print(f"✅ 生成成功:")
        print(f"   教师: {len(result.get('teachers', []))}")
        print(f"   课程: {len(result.get('courses', []))}")
        print(f"   排课: {len(result.get('schedules', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本生成测试失败: {e}")
        return False

def test_quality_validation():
    """测试质量验证"""
    print("\n🧪 测试质量验证...")
    
    try:
        from data_quality_validator import DataQualityAssessment
        
        # 模拟测试数据
        test_data = {
            'teachers': [
                {'teacher_id': 'T001', 'name': '张教授', 'title': '教授', 'department': '计算机学院'},
                {'teacher_id': 'T002', 'name': '李副教授', 'title': '副教授', 'department': '数学学院'}
            ],
            'courses': [
                {'course_id': 'C001', 'name': '高等数学', 'type': '必修课', 'credits': 4, 'department': '数学学院'},
                {'course_id': 'C002', 'name': '程序设计', 'type': '必修课', 'credits': 3, 'department': '计算机学院'}
            ],
            'schedules': [
                {'course_id': 'C001', 'teacher_id': 'T001', 'classroom_id': 'R001', 'time_slot': '08:00-08:45'},
                {'course_id': 'C002', 'teacher_id': 'T002', 'classroom_id': 'R002', 'time_slot': '09:00-09:45'}
            ]
        }
        
        assessor = DataQualityAssessment()
        report = assessor.assess_quality(test_data)
        
        print(f"✅ 质量评估成功:")
        print(f"   总体得分: {report.overall_score:.3f}")
        print(f"   问题数量: {report.total_issues}")
        
        return True
        
    except Exception as e:
        print(f"❌ 质量验证测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 百万级课程数据生成器快速测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_import),
        ("基本数据生成", test_basic_generation),
        ("质量验证", test_quality_validation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append(False)
    
    # 汇总结果
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统已就绪。")
        
        # 运行简单示例
        print("\n🎯 运行简单生成示例...")
        try:
            from realistic_course_generator import create_generation_config, generate_realistic_course_data
            import argparse
            
            # 模拟命令行参数
            class Args:
                students = 100
                teachers = 10
                courses = 50
                schedules = 200
                semesters = 4
                realism_level = 0.8
                constraint_strictness = 0.9
                disable_prerequisites = False
                disable_time_conflicts = False
                disable_capacity = False
                disable_workload = False
                
            args = Args()
            config = create_generation_config(args)
            
            print(f"✨ 配置创建成功，目标数据规模:")
            print(f"   学生: {config.target_students}")
            print(f"   教师: {config.target_teachers}")
            print(f"   课程: {config.target_courses}")
            
            print("\n💡 使用提示:")
            print("   运行完整测试: python test_realistic_generation.py")
            print("   生成小规模数据: python realistic_course_generator.py --students 1000")
            print("   生成百万级数据: python realistic_course_generator.py --students 1000000")
            
        except Exception as e:
            print(f"⚠️ 示例运行失败，但核心功能正常: {e}")
        
        return True
    else:
        print("❌ 部分测试失败，请检查系统配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)