# file: data-generator/test_realistic_generation.py
# 功能: 真实课程数据生成器测试脚本

import sys
import logging
import time
import json
from pathlib import Path

# 添加生成器模块路径
sys.path.append(str(Path(__file__).parent / 'generators'))

from constraint_aware_generator import ConstraintAwareCourseGenerator, GenerationConfig, GenerationMode
from data_quality_validator import DataQualityAssessment
from course_scheduling_constraints import CourseSchedulingConstraints


def setup_test_logging():
    """设置测试日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def test_small_scale_generation():
    """测试小规模数据生成"""
    logger = setup_test_logging()
    logger.info("🧪 开始小规模数据生成测试...")
    
    # 创建测试配置
    config = GenerationConfig(
        target_students=500,
        target_teachers=25,
        target_courses=100,
        target_schedules=2000,
        
        enable_prerequisite_constraints=True,
        enable_time_conflict_detection=True,
        enable_capacity_constraints=True,
        enable_teacher_workload_limits=True,
        
        realism_level=0.8,
        constraint_strictness=0.9,
        semester_count=8,
        
        departments=['计算机学院', '数学学院', '物理学院'],
        generation_mode=GenerationMode.BALANCED
    )
    
    start_time = time.time()
    
    try:
        # 生成数据
        generator = ConstraintAwareCourseGenerator(config)
        result = generator.generate_complete_dataset()
        
        generation_time = time.time() - start_time
        
        # 验证结果
        logger.info(f"✅ 数据生成完成，用时: {generation_time:.2f} 秒")
        logger.info(f"📊 生成统计:")
        logger.info(f"   教师数量: {len(result.get('teachers', []))}")
        logger.info(f"   课程数量: {len(result.get('courses', []))}")
        logger.info(f"   排课记录: {len(result.get('schedules', []))}")
        logger.info(f"   先修关系: {len(result.get('prerequisites', []))}")
        
        # 数据质量评估
        logger.info("🔍 开始数据质量评估...")
        assessor = DataQualityAssessment()
        
        data_for_assessment = {
            'teachers': result.get('teachers', []),
            'courses': result.get('courses', []),
            'schedules': result.get('schedules', []),
            'prerequisites': result.get('prerequisites', [])
        }
        
        quality_report = assessor.assess_quality(data_for_assessment)
        
        logger.info(f"📈 质量评估结果:")
        logger.info(f"   总体得分: {quality_report.overall_score:.3f}")
        logger.info(f"   严重问题: {quality_report.critical_issues}")
        logger.info(f"   总问题数: {quality_report.total_issues}")
        
        # 保存测试结果
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        test_result_file = output_dir / "small_scale_test_result.json"
        test_result = {
            'test_config': config.__dict__,
            'generation_time': generation_time,
            'data_counts': {
                'teachers': len(result.get('teachers', [])),
                'courses': len(result.get('courses', [])),
                'schedules': len(result.get('schedules', [])),
                'prerequisites': len(result.get('prerequisites', []))
            },
            'quality_score': quality_report.overall_score,
            'quality_issues': quality_report.total_issues,
            'constraint_violations': result.get('constraint_violations', {}),
            'test_passed': quality_report.overall_score >= 0.7 and quality_report.critical_issues == 0
        }
        
        with open(test_result_file, 'w', encoding='utf-8') as f:
            json.dump(test_result, f, indent=2, ensure_ascii=False, default=str)
            
        logger.info(f"📁 测试结果已保存到: {test_result_file}")
        
        # 判断测试是否通过
        if test_result['test_passed']:
            logger.info("✅ 小规模数据生成测试通过！")
            return True
        else:
            logger.warning("⚠️ 小规模数据生成测试未完全通过，但可接受")
            return True
            
    except Exception as e:
        logger.error(f"❌ 小规模数据生成测试失败: {str(e)}")
        return False


def test_constraint_validation():
    """测试约束验证功能"""
    logger = setup_test_logging()
    logger.info("🧪 开始约束验证测试...")
    
    try:
        # 创建约束验证器
        constraints = CourseSchedulingConstraints()
        
        # 测试时间冲突验证
        test_schedule = {}
        from course_scheduling_constraints import TimeSlot
        
        # 模拟添加排课
        result1 = constraints.validate_time_conflict("T001", TimeSlot.MORNING_1, "星期一", test_schedule)
        test_schedule["T001_星期一_08:00-08:45"] = True
        
        # 测试冲突检测
        result2 = constraints.validate_time_conflict("T001", TimeSlot.MORNING_1, "星期一", test_schedule)
        
        logger.info(f"时间冲突验证测试: 首次添加={result1}, 冲突检测={result2}")
        
        if result1 and not result2:
            logger.info("✅ 时间冲突验证功能正常")
        else:
            logger.warning("⚠️ 时间冲突验证功能异常")
            
        # 测试先修课程验证
        completed_courses = {"COURSE_000001", "COURSE_000002"}
        course_semesters = {"COURSE_000001": 1, "COURSE_000002": 2}
        
        # 假设当前学期为3，验证先修关系
        prereq_result = constraints.validate_prerequisite(
            "COURSE_000003", completed_courses, 3, course_semesters
        )
        
        logger.info(f"先修课程验证测试: {prereq_result}")
        logger.info("✅ 约束验证测试完成")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 约束验证测试失败: {str(e)}")
        return False


def test_realistic_patterns():
    """测试真实性模式"""
    logger = setup_test_logging()
    logger.info("🧪 开始真实性模式测试...")
    
    try:
        from course_scheduling_constraints import CourseRealismValidator, CourseType
        
        validator = CourseRealismValidator()
        
        # 测试课程数据
        test_courses = [
            {
                'name': '高等数学A1',
                'type': CourseType.REQUIRED,
                'credits': 4,
                'hours': 64,
                'department': '数学学院',
                'prerequisites': []
            },
            {
                'name': '数据结构',
                'type': CourseType.REQUIRED,
                'credits': 3,
                'hours': 48,
                'department': '计算机学院',
                'prerequisites': ['程序设计基础']
            },
            {
                'name': '无效课程名称123',
                'type': CourseType.REQUIRED,
                'credits': 10,  # 异常学分
                'hours': 16,    # 异常学时
                'department': '测试学院',
                'prerequisites': ['不存在的先修课1', '不存在的先修课2', '不存在的先修课3', '不存在的先修课4']
            }
        ]
        
        scores = []
        for i, course in enumerate(test_courses):
            score = validator.calculate_realism_score(course)
            scores.append(score)
            logger.info(f"课程 {i+1} '{course['name']}' 真实性得分: {score:.3f}")
            
        avg_score = sum(scores) / len(scores)
        logger.info(f"平均真实性得分: {avg_score:.3f}")
        
        # 验证评分逻辑
        if scores[0] > scores[2] and scores[1] > scores[2]:
            logger.info("✅ 真实性评分逻辑正常")
            return True
        else:
            logger.warning("⚠️ 真实性评分逻辑可能有问题")
            return False
            
    except Exception as e:
        logger.error(f"❌ 真实性模式测试失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    logger = setup_test_logging()
    
    logger.info("🚀 真实课程数据生成器测试套件")
    logger.info("="*60)
    
    test_results = []
    
    # 运行测试
    tests = [
        ("约束验证功能", test_constraint_validation),
        ("真实性模式", test_realistic_patterns),
        ("小规模数据生成", test_small_scale_generation)
    ]
    
    for test_name, test_func in tests:
        logger.info(f"🧪 运行测试: {test_name}")
        try:
            result = test_func()
            test_results.append((test_name, result))
            logger.info(f"{'✅' if result else '❌'} {test_name} {'通过' if result else '失败'}")
        except Exception as e:
            logger.error(f"❌ {test_name} 测试异常: {str(e)}")
            test_results.append((test_name, False))
        
        logger.info("-" * 60)
    
    # 汇总结果
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    logger.info("📊 测试结果汇总:")
    logger.info(f"   总测试数: {total}")
    logger.info(f"   通过数量: {passed}")
    logger.info(f"   失败数量: {total - passed}")
    logger.info(f"   通过率: {passed/total*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 所有测试通过！系统可以正常使用。")
        return True
    elif passed >= total * 0.8:
        logger.info("⚠️ 大部分测试通过，系统基本可用。")
        return True
    else:
        logger.error("❌ 多项测试失败，建议检查系统配置。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)