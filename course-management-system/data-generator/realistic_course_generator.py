# file: data-generator/realistic_course_generator.py
# 功能: 真实课程数据生成器主程序

import sys
import logging
import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any

# 添加生成器模块路径
sys.path.append(str(Path(__file__).parent / 'generators'))

from constraint_aware_generator import ConstraintAwareCourseGenerator, GenerationConfig, GenerationMode
from mega_scale_processor import MegaScaleDataGenerator, BatchConfig, ProcessingMode, MemoryStrategy
from data_quality_validator import DataQualityAssessment
from course_scheduling_constraints import CourseRealismValidator
from teacher_course_matching import generate_realistic_teacher_profiles


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('course_generation.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)


def create_generation_config(args) -> GenerationConfig:
    """创建生成配置"""
    return GenerationConfig(
        target_students=args.students,
        target_teachers=args.teachers,
        target_courses=args.courses,
        target_schedules=args.schedules,
        
        enable_prerequisite_constraints=not args.disable_prerequisites,
        enable_time_conflict_detection=not args.disable_time_conflicts,
        enable_capacity_constraints=not args.disable_capacity,
        enable_teacher_workload_limits=not args.disable_workload,
        
        realism_level=args.realism_level,
        constraint_strictness=args.constraint_strictness,
        semester_count=args.semesters,
        
        departments=[
            '计算机科学与技术学院', '数学与统计学院', '物理与电子学院',
            '外国语学院', '经济管理学院', '机械工程学院'
        ],
        
        generation_mode=GenerationMode.BALANCED
    )


def create_batch_config(args) -> BatchConfig:
    """创建批处理配置"""
    return BatchConfig(
        batch_size=args.batch_size,
        max_memory_mb=args.max_memory,
        memory_threshold=args.memory_threshold,
        gc_frequency=args.gc_frequency,
        checkpoint_interval=args.checkpoint_interval,
        compression_enabled=not args.disable_compression,
        
        max_workers=args.workers,
        processing_mode=ProcessingMode.HYBRID,
        memory_strategy=MemoryStrategy.BALANCED,
        
        enable_object_pool=True,
        enable_streaming=True,
        
        checkpoint_dir="checkpoints",
        auto_resume=args.auto_resume,
        cleanup_checkpoints=True
    )


def generate_realistic_course_data(generation_config: GenerationConfig, 
                                 batch_config: BatchConfig,
                                 output_dir: str,
                                 logger: logging.Logger) -> Dict[str, Any]:
    """生成真实的课程数据"""
    
    logger.info("="*80)
    logger.info("🎓 真实课程数据生成系统启动")
    logger.info("="*80)
    
    # 打印配置信息
    logger.info(f"📊 目标规模:")
    logger.info(f"   学生数量: {generation_config.target_students:,}")
    logger.info(f"   教师数量: {generation_config.target_teachers:,}")
    logger.info(f"   课程数量: {generation_config.target_courses:,}")
    logger.info(f"   排课记录: {generation_config.target_schedules:,}")
    
    logger.info(f"⚙️ 处理配置:")
    logger.info(f"   批次大小: {batch_config.batch_size:,}")
    logger.info(f"   最大内存: {batch_config.max_memory_mb}MB")
    logger.info(f"   工作进程: {batch_config.max_workers}")
    logger.info(f"   处理模式: {batch_config.processing_mode.value}")
    
    start_time = time.time()
    
    try:
        # 判断是否需要大规模处理
        if generation_config.target_students >= 50000:
            logger.info("🚀 启动百万级数据生成模式...")
            generator = MegaScaleDataGenerator(generation_config, batch_config)
            result = generator.generate_mega_dataset(output_dir)
        else:
            logger.info("🎯 启动标准数据生成模式...")
            generator = ConstraintAwareCourseGenerator(generation_config)
            result = generator.generate_complete_dataset()
            
            # 保存结果
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            output_file = output_path / "course_dataset.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                
            logger.info(f"📁 数据已保存到: {output_file}")
            
        generation_time = time.time() - start_time
        
        # 数据质量评估
        logger.info("🔍 开始数据质量评估...")
        quality_assessor = DataQualityAssessment()
        
        # 提取数据用于质量评估
        if isinstance(result, dict) and 'output_directory' in result:
            # 大规模生成的结果
            data_for_assessment = {
                'teachers': result.get('data_summary', {}).get('total_teachers', 0),
                'courses': result.get('data_summary', {}).get('total_courses', 0),
                'schedules': result.get('data_summary', {}).get('total_schedules', 0)
            }
            quality_report = None  # 大规模数据跳过详细质量评估
        else:
            # 标准生成的结果
            data_for_assessment = {
                'teachers': result.get('teachers', []),
                'courses': result.get('courses', []),
                'schedules': result.get('schedules', []),
                'prerequisites': result.get('prerequisites', [])
            }
            quality_report = quality_assessor.assess_quality(data_for_assessment, sampling_rate=0.1)
            
        # 生成综合报告
        final_report = {
            'generation_summary': {
                'total_time_seconds': generation_time,
                'generation_mode': generation_config.generation_mode.value,
                'processing_mode': batch_config.processing_mode.value,
                'constraint_compliance': {
                    'prerequisites_enabled': generation_config.enable_prerequisite_constraints,
                    'time_conflicts_enabled': generation_config.enable_time_conflict_detection,
                    'capacity_enabled': generation_config.enable_capacity_constraints,
                    'workload_enabled': generation_config.enable_teacher_workload_limits
                }
            },
            'data_statistics': result.get('data_summary', {}),
            'quality_assessment': quality_report.__dict__ if quality_report else None,
            'constraint_violations': result.get('constraint_violations', {}),
            'generation_config': generation_config.__dict__,
            'batch_config': batch_config.__dict__
        }
        
        # 保存综合报告
        report_file = Path(output_dir) / "generation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False, default=str)
            
        # 打印总结
        logger.info("="*80)
        logger.info("✅ 数据生成完成")
        logger.info("="*80)
        logger.info(f"⏱️ 总用时: {generation_time:.2f} 秒")
        
        if quality_report:
            logger.info(f"📈 数据质量得分: {quality_report.overall_score:.3f}")
            logger.info(f"🔴 严重问题: {quality_report.critical_issues} 个")
            logger.info(f"⚠️ 总问题数: {quality_report.total_issues} 个")
            
        logger.info(f"📊 数据统计:")
        if isinstance(result, dict):
            if 'data_summary' in result:
                stats = result['data_summary']
                for key, value in stats.items():
                    if isinstance(value, (int, float)):
                        logger.info(f"   {key}: {value:,}")
            else:
                logger.info(f"   教师: {len(result.get('teachers', []))}")
                logger.info(f"   课程: {len(result.get('courses', []))}")
                logger.info(f"   排课: {len(result.get('schedules', []))}")
                
        logger.info(f"📁 输出目录: {output_dir}")
        logger.info(f"📋 详细报告: {report_file}")
        
        if quality_report and quality_report.recommendations:
            logger.info("💡 改进建议:")
            for rec in quality_report.recommendations:
                logger.info(f"   • {rec}")
                
        return final_report
        
    except Exception as e:
        logger.error(f"❌ 数据生成失败: {str(e)}")
        raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='真实课程数据生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 生成小规模测试数据
  python realistic_course_generator.py --students 1000 --teachers 50 --courses 200
  
  # 生成中等规模数据
  python realistic_course_generator.py --students 50000 --teachers 2500 --courses 5000
  
  # 生成百万级数据
  python realistic_course_generator.py --students 1000000 --teachers 50000 --courses 100000
  
  # 自定义约束设置
  python realistic_course_generator.py --students 10000 --realism-level 0.9 --constraint-strictness 0.8
        """
    )
    
    # 数据规模参数
    parser.add_argument('--students', type=int, default=10000,
                       help='目标学生数量 (默认: 10000)')
    parser.add_argument('--teachers', type=int, default=500,
                       help='目标教师数量 (默认: 500)')
    parser.add_argument('--courses', type=int, default=1000,
                       help='目标课程数量 (默认: 1000)')
    parser.add_argument('--schedules', type=int, default=50000,
                       help='目标排课记录数量 (默认: 50000)')
    parser.add_argument('--semesters', type=int, default=8,
                       help='学期数量 (默认: 8)')
    
    # 质量参数
    parser.add_argument('--realism-level', type=float, default=0.8,
                       help='真实性要求等级 0-1 (默认: 0.8)')
    parser.add_argument('--constraint-strictness', type=float, default=0.9,
                       help='约束严格程度 0-1 (默认: 0.9)')
    
    # 约束开关
    parser.add_argument('--disable-prerequisites', action='store_true',
                       help='禁用先修课程约束')
    parser.add_argument('--disable-time-conflicts', action='store_true',
                       help='禁用时间冲突检测')
    parser.add_argument('--disable-capacity', action='store_true',
                       help='禁用容量约束')
    parser.add_argument('--disable-workload', action='store_true',
                       help='禁用教师工作负荷限制')
    
    # 性能参数
    parser.add_argument('--batch-size', type=int, default=2000,
                       help='批处理大小 (默认: 2000)')
    parser.add_argument('--max-memory', type=int, default=4096,
                       help='最大内存限制MB (默认: 4096)')
    parser.add_argument('--memory-threshold', type=float, default=0.8,
                       help='内存使用率阈值 (默认: 0.8)')
    parser.add_argument('--workers', type=int, default=4,
                       help='并行工作进程数 (默认: 4)')
    parser.add_argument('--gc-frequency', type=int, default=5,
                       help='垃圾回收频率 (默认: 5)')
    parser.add_argument('--checkpoint-interval', type=int, default=10000,
                       help='检查点保存间隔 (默认: 10000)')
    
    # 其他参数
    parser.add_argument('--output', '-o', default='course_data_output',
                       help='输出目录 (默认: course_data_output)')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别 (默认: INFO)')
    parser.add_argument('--disable-compression', action='store_true',
                       help='禁用压缩')
    parser.add_argument('--auto-resume', action='store_true',
                       help='自动从检查点恢复')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging(args.log_level)
    
    try:
        # 创建配置
        generation_config = create_generation_config(args)
        batch_config = create_batch_config(args)
        
        # 生成数据
        result = generate_realistic_course_data(
            generation_config=generation_config,
            batch_config=batch_config,
            output_dir=args.output,
            logger=logger
        )
        
        logger.info("🎉 程序执行成功完成！")
        
    except KeyboardInterrupt:
        logger.warning("⚠️ 用户中断程序执行")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()