# file: data-generator/main.py
# 功能: 主数据生成脚本

import argparse
import sys
import time
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from config import DATA_SCALE_CONFIG, GenerationConfig
from generators import (
    DepartmentGenerator,
    UserGenerator,
    CourseGenerator,
    FacilityGenerator,
    ComplexScenarioGenerator,
    DataExporter
)


def generate_complete_dataset(scale: str = 'large', 
                            output_formats: List[str] = None,
                            output_dir: str = 'output',
                            validate_data: bool = True,
                            include_conflicts: bool = True) -> Dict[str, Any]:
    """生成完整的测试数据集
    
    Args:
        scale: 数据规模 ('large', 'medium', 'small')
        output_formats: 输出格式列表 (['json', 'sql'])
        output_dir: 输出目录
        validate_data: 是否验证数据
        include_conflicts: 是否包含冲突场景
        
    Returns:
        生成的数据集字典
    """
    if output_formats is None:
        output_formats = ['json']
    
    # 验证规模参数
    if scale not in DATA_SCALE_CONFIG:
        raise ValueError(f"不支持的数据规模: {scale}。支持的规模: {list(DATA_SCALE_CONFIG.keys())}")
    
    config = DATA_SCALE_CONFIG[scale]
    
    print(f"🚀 开始生成 {scale} 规模测试数据...")
    print(f"📊 数据规模配置: {config}")
    print("-" * 60)
    
    start_time = time.time()
    
    # 初始化生成器
    print("🔧 初始化数据生成器...")
    dept_gen = DepartmentGenerator()
    user_gen = UserGenerator()
    course_gen = CourseGenerator()
    facility_gen = FacilityGenerator()
    scenario_gen = ComplexScenarioGenerator()
    exporter = DataExporter(output_dir)
    
    # 生成基础数据
    print("\n📚 生成院系专业数据...")
    departments = dept_gen.generate_departments(config['departments'])
    majors = dept_gen.generate_majors(departments)
    print(f"   ✅ 生成 {len(departments)} 个院系，{len(majors)} 个专业")
    
    print("\n👥 生成用户数据...")
    students = user_gen.generate_students(config['students'], majors)
    teachers = user_gen.generate_teachers(config['teachers'], departments)
    print(f"   ✅ 生成 {len(students)} 名学生，{len(teachers)} 名教师")
    
    print("\n📖 生成课程数据...")
    courses = course_gen.generate_courses(config['courses'], departments, teachers)
    print(f"   ✅ 生成 {len(courses)} 门课程")
    
    print("\n🏢 生成设施数据...")
    classrooms = facility_gen.generate_classrooms(config['classrooms'])
    time_slots = facility_gen.generate_time_slots()
    print(f"   ✅ 生成 {len(classrooms)} 间教室，{len(time_slots)} 个时间段")
    
    print("\n🎯 生成复杂场景数据...")
    enrollments = scenario_gen.generate_enrollment_data(students, courses)
    teacher_preferences = scenario_gen.generate_teacher_preferences(teachers, time_slots)
    print(f"   ✅ 生成 {len(enrollments)} 条选课记录，{len(teacher_preferences)} 条教师偏好")
    
    conflicts = []
    constraints = []
    if include_conflicts:
        conflicts = scenario_gen.generate_conflict_scenarios(courses, teachers, classrooms, students)
        constraints = scenario_gen.generate_scheduling_constraints(courses, teachers, classrooms)
        print(f"   ✅ 生成 {len(conflicts)} 个冲突场景，{len(constraints)} 个约束条件")
    
    # 组装完整数据集
    dataset = {
        'departments': departments,
        'majors': majors,
        'students': students,
        'teachers': teachers,
        'courses': courses,
        'classrooms': classrooms,
        'time_slots': time_slots,
        'enrollments': enrollments,
        'teacher_preferences': teacher_preferences,
        'conflicts': conflicts,
        'constraints': constraints,
    }

    # 计算总记录数
    total_records = sum(len(v) if isinstance(v, list) else 0 for v in dataset.values() if v)

    # 添加元数据
    dataset['metadata'] = {
        'scale': scale,
        'generated_at': datetime.now().isoformat(),
        'generator_version': '1.0.0',
        'config': config,
        'total_records': total_records,
        'generation_time_seconds': 0,  # 将在后面更新
        'validation_passed': False,  # 将在验证后更新
        'output_formats': output_formats,
        'include_conflicts': include_conflicts
    }
    
    generation_time = time.time() - start_time
    dataset['metadata']['generation_time_seconds'] = round(generation_time, 2)
    
    total_records = dataset['metadata']['total_records']
    print(f"\n✨ 数据生成完成！")
    print(f"   📊 总计 {total_records:,} 条记录")
    print(f"   ⏱️  耗时 {generation_time:.2f} 秒")
    print(f"   🚀 生成速度 {total_records/generation_time:.0f} 条/秒")
    
    # 数据验证
    validation_errors = {}
    if validate_data:
        print("\n🔍 验证数据完整性...")
        validation_start = time.time()
        validation_errors = exporter.validate_data_integrity(dataset)
        validation_time = time.time() - validation_start
        
        if validation_errors and any(validation_errors.values()):
            print(f"   ⚠️  发现 {sum(len(errors) for errors in validation_errors.values())} 个问题")
            for table, errors in validation_errors.items():
                if errors:
                    print(f"      - {table}: {len(errors)} 个问题")
            dataset['metadata']['validation_passed'] = False
        else:
            print(f"   ✅ 数据验证通过 (耗时 {validation_time:.2f} 秒)")
            dataset['metadata']['validation_passed'] = True
    
    # 导出数据
    if output_formats:
        print(f"\n💾 导出数据 (格式: {', '.join(output_formats)})...")
        export_start = time.time()
        
        exported_files = []
        if 'json' in output_formats:
            json_file = exporter.export_to_json(dataset)
            exported_files.append(json_file)
        
        if 'sql' in output_formats:
            sql_file = exporter.export_to_sql(dataset)
            exported_files.append(sql_file)
        
        # 生成数据报告
        report_file = exporter.generate_data_report(dataset, validation_errors)
        exported_files.append(report_file)
        
        export_time = time.time() - export_start
        print(f"   ✅ 导出完成 (耗时 {export_time:.2f} 秒)")
        print(f"   📁 文件列表:")
        for file_path in exported_files:
            print(f"      - {file_path}")
    
    total_time = time.time() - start_time
    print(f"\n🎉 全部完成！总耗时 {total_time:.2f} 秒")
    print("-" * 60)
    
    return dataset


def main(args=None):
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description='校园课程表管理系统测试数据生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py --scale large --format json sql
  python main.py --scale medium --output-dir ./data --no-validate
  python main.py --scale small --no-conflicts
        """
    )
    
    parser.add_argument(
        '--scale', '-s',
        choices=['large', 'medium', 'small'],
        default='medium',
        help='数据规模 (默认: medium)'
    )
    
    parser.add_argument(
        '--format', '-f',
        nargs='+',
        choices=['json', 'sql'],
        default=['json'],
        help='输出格式 (默认: json)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='output',
        help='输出目录 (默认: output)'
    )
    
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='跳过数据验证'
    )
    
    parser.add_argument(
        '--no-conflicts',
        action='store_true',
        help='不生成冲突场景数据'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='静默模式，减少输出'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='数据生成器 v1.0.0'
    )
    
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    # 设置输出级别
    if parsed_args.quiet:
        import logging
        logging.basicConfig(level=logging.WARNING)
    
    try:
        # 生成数据
        dataset = generate_complete_dataset(
            scale=parsed_args.scale,
            output_formats=parsed_args.format,
            output_dir=parsed_args.output_dir,
            validate_data=not parsed_args.no_validate,
            include_conflicts=not parsed_args.no_conflicts
        )
        
        if not parsed_args.quiet:
            print("\n🎯 数据生成任务完成！")
            print(f"   规模: {parsed_args.scale}")
            print(f"   记录数: {dataset['metadata']['total_records']:,}")
            print(f"   输出目录: {parsed_args.output_dir}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        if not parsed_args.quiet:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
