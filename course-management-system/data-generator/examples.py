# file: data-generator/examples.py
# 功能: 使用示例和演示代码

"""
校园课程表管理系统数据生成器使用示例

本文件包含各种使用场景的示例代码，帮助用户快速上手。
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from main import generate_complete_dataset
from generators import (
    DepartmentGenerator,
    UserGenerator,
    CourseGenerator,
    FacilityGenerator,
    ComplexScenarioGenerator,
    DataExporter
)


def example_basic_usage():
    """示例1: 基本使用方法"""
    print("=" * 60)
    print("示例1: 基本使用方法")
    print("=" * 60)
    
    # 生成小规模测试数据
    print("生成小规模测试数据...")
    dataset = generate_complete_dataset(
        scale='small',
        output_formats=['json'],
        validate_data=True
    )
    
    # 查看生成的数据统计
    print(f"\n数据统计:")
    print(f"- 院系: {len(dataset['departments'])} 个")
    print(f"- 专业: {len(dataset['majors'])} 个")
    print(f"- 学生: {len(dataset['students'])} 名")
    print(f"- 教师: {len(dataset['teachers'])} 名")
    print(f"- 课程: {len(dataset['courses'])} 门")
    print(f"- 教室: {len(dataset['classrooms'])} 间")
    print(f"- 选课记录: {len(dataset['enrollments'])} 条")
    
    return dataset


def example_individual_generators():
    """示例2: 单独使用各个生成器"""
    print("\n" + "=" * 60)
    print("示例2: 单独使用各个生成器")
    print("=" * 60)
    
    # 1. 生成院系专业数据
    print("\n1. 生成院系专业数据")
    dept_gen = DepartmentGenerator()
    departments = dept_gen.generate_departments(3)
    majors = dept_gen.generate_majors(departments)
    
    print(f"生成了 {len(departments)} 个院系:")
    for dept in departments:
        print(f"  - {dept['name']} ({dept['code']})")
    
    print(f"生成了 {len(majors)} 个专业:")
    for major in majors[:5]:  # 只显示前5个
        print(f"  - {major['name']} (院系ID: {major['department_id']})")
    
    # 2. 生成用户数据
    print("\n2. 生成用户数据")
    user_gen = UserGenerator()
    students = user_gen.generate_students(20, majors)
    teachers = user_gen.generate_teachers(5, departments)
    
    print(f"生成了 {len(students)} 名学生:")
    for student in students[:3]:  # 只显示前3个
        print(f"  - {student['name']} ({student['student_id']})")
    
    print(f"生成了 {len(teachers)} 名教师:")
    for teacher in teachers:
        print(f"  - {teacher['name']} ({teacher['title']})")
    
    # 3. 生成课程数据
    print("\n3. 生成课程数据")
    course_gen = CourseGenerator()
    courses = course_gen.generate_courses(10, departments, teachers)
    
    print(f"生成了 {len(courses)} 门课程:")
    for course in courses[:5]:  # 只显示前5门
        print(f"  - {course['name']} ({course['credits']}学分)")
    
    return {
        'departments': departments,
        'majors': majors,
        'students': students,
        'teachers': teachers,
        'courses': courses
    }


def example_data_validation():
    """示例3: 数据验证和质量检查"""
    print("\n" + "=" * 60)
    print("示例3: 数据验证和质量检查")
    print("=" * 60)
    
    # 生成测试数据
    dataset = generate_complete_dataset(
        scale='small',
        output_formats=[],  # 不输出文件
        validate_data=False  # 先不验证，我们手动验证
    )
    
    # 使用导出器进行验证
    exporter = DataExporter()
    print("正在验证数据完整性...")
    
    errors = exporter.validate_data_integrity(dataset)
    
    if errors:
        print("发现以下问题:")
        for table_name, error_list in errors.items():
            print(f"\n{table_name} ({len(error_list)} 个问题):")
            for error in error_list[:3]:  # 只显示前3个错误
                print(f"  - {error}")
            if len(error_list) > 3:
                print(f"  - ... 还有 {len(error_list) - 3} 个问题")
    else:
        print("✅ 数据验证通过，未发现问题！")
    
    # 生成数据报告
    print("\n生成数据质量报告...")
    report_file = exporter.generate_data_report(dataset, errors)
    print(f"报告已保存到: {report_file}")


def example_custom_configuration():
    """示例4: 自定义配置"""
    print("\n" + "=" * 60)
    print("示例4: 自定义配置")
    print("=" * 60)
    
    # 创建自定义规模的数据
    print("使用自定义配置生成数据...")
    
    # 修改配置（这里只是演示，实际使用时应该修改config.py）
    from config import DATA_SCALE_CONFIG
    
    # 临时添加自定义配置
    DATA_SCALE_CONFIG['custom'] = {
        'students': 100,
        'teachers': 10,
        'courses': 50,
        'classrooms': 10,
        'departments': 2,
        'majors': 6,
        'semesters': 8,
        'time_slots': 10,
        'weeks_per_semester': 16,
    }
    
    try:
        dataset = generate_complete_dataset(
            scale='custom',
            output_formats=['json'],
            validate_data=True
        )
        
        print("自定义规模数据生成成功！")
        print(f"总记录数: {dataset['metadata']['total_records']}")
        
    except ValueError as e:
        print(f"配置错误: {e}")
    finally:
        # 清理临时配置
        if 'custom' in DATA_SCALE_CONFIG:
            del DATA_SCALE_CONFIG['custom']


def example_conflict_analysis():
    """示例5: 冲突场景分析"""
    print("\n" + "=" * 60)
    print("示例5: 冲突场景分析")
    print("=" * 60)
    
    # 生成包含冲突的数据
    dataset = generate_complete_dataset(
        scale='small',
        output_formats=[],
        include_conflicts=True
    )
    
    conflicts = dataset.get('conflicts', [])
    print(f"检测到 {len(conflicts)} 个潜在冲突:")
    
    # 按类型统计冲突
    conflict_types = {}
    for conflict in conflicts:
        conflict_type = conflict['type']
        conflict_types[conflict_type] = conflict_types.get(conflict_type, 0) + 1
    
    print("\n冲突类型分布:")
    for conflict_type, count in conflict_types.items():
        print(f"  - {conflict_type}: {count} 个")
    
    # 显示高严重性冲突
    high_severity_conflicts = [c for c in conflicts if c.get('severity') == 'high']
    print(f"\n高严重性冲突 ({len(high_severity_conflicts)} 个):")
    for conflict in high_severity_conflicts[:3]:  # 只显示前3个
        print(f"  - {conflict['description']}")
        print(f"    建议: {conflict.get('suggested_solution', '无')}")


def example_performance_test():
    """示例6: 性能测试"""
    print("\n" + "=" * 60)
    print("示例6: 性能测试")
    print("=" * 60)
    
    import time
    
    scales = ['small']  # 只测试小规模以节省时间
    
    for scale in scales:
        print(f"\n测试 {scale} 规模数据生成性能...")
        
        start_time = time.time()
        dataset = generate_complete_dataset(
            scale=scale,
            output_formats=[],
            validate_data=False  # 跳过验证以测试纯生成性能
        )
        end_time = time.time()
        
        generation_time = end_time - start_time
        total_records = dataset['metadata']['total_records']
        speed = total_records / generation_time if generation_time > 0 else 0
        
        print(f"  规模: {scale}")
        print(f"  记录数: {total_records:,}")
        print(f"  耗时: {generation_time:.2f} 秒")
        print(f"  速度: {speed:.0f} 条/秒")


def example_export_formats():
    """示例7: 不同导出格式"""
    print("\n" + "=" * 60)
    print("示例7: 不同导出格式")
    print("=" * 60)
    
    # 生成数据
    dataset = generate_complete_dataset(
        scale='small',
        output_formats=[],  # 先不导出
        validate_data=False
    )
    
    # 使用导出器导出不同格式
    exporter = DataExporter('example_output')
    
    print("导出JSON格式...")
    json_file = exporter.export_to_json(dataset, 'example_data.json')
    
    print("导出SQL格式...")
    sql_file = exporter.export_to_sql(dataset, 'example_data.sql')
    
    print("生成数据报告...")
    report_file = exporter.generate_data_report(dataset)
    
    print(f"\n导出完成:")
    print(f"  JSON文件: {json_file}")
    print(f"  SQL文件: {sql_file}")
    print(f"  报告文件: {report_file}")


def main():
    """运行所有示例"""
    print("🚀 校园课程表管理系统数据生成器示例")
    print("本示例将演示各种使用场景和功能")
    
    try:
        # 运行各个示例
        example_basic_usage()
        example_individual_generators()
        example_data_validation()
        example_custom_configuration()
        example_conflict_analysis()
        example_performance_test()
        example_export_formats()
        
        print("\n" + "=" * 60)
        print("🎉 所有示例运行完成！")
        print("=" * 60)
        print("\n查看生成的文件:")
        print("- output/json/ - JSON格式数据")
        print("- output/sql/ - SQL格式数据")
        print("- output/reports/ - 数据质量报告")
        print("- example_output/ - 示例导出文件")
        
    except Exception as e:
        print(f"\n❌ 示例运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
