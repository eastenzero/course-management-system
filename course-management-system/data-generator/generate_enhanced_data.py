#!/usr/bin/env python3
"""
使用修正的main.py脚本生成更大规模的数据
"""

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

# 定义扩大的数据规模配置
ENHANCED_DATA_SCALE_CONFIG = {
    'small': {
        'departments': 5,
        'students': 1000,
        'teachers': 50,
        'courses': 100,
        'classrooms': 20,
    },
    'medium': {
        'departments': 10,
        'students': 5000,
        'teachers': 200,
        'courses': 500,
        'classrooms': 50,
    },
    'large': {
        'departments': 15,
        'students': 25000,     # 从10000扩大到25000
        'teachers': 1200,      # 从500扩大到1200
        'courses': 3000,       # 从1000扩大到3000
        'classrooms': 150,     # 从80扩大到150
    },
    'huge': {
        'departments': 20,
        'students': 50000,     # 50000学生
        'teachers': 2500,      # 2500教师
        'courses': 6000,       # 6000课程
        'classrooms': 300,     # 300教室
    }
}

def generate_enhanced_dataset(scale: str = 'large', 
                            output_formats: List[str] = None,
                            output_dir: str = 'enhanced_output',
                            validate_data: bool = True,
                            include_conflicts: bool = True) -> Dict[str, Any]:
    """生成增强规模的测试数据集"""
    if output_formats is None:
        output_formats = ['json', 'sql']
    
    # 使用增强的数据规模配置
    config = ENHANCED_DATA_SCALE_CONFIG.get(scale, ENHANCED_DATA_SCALE_CONFIG['large'])
    
    print(f"🚀 开始生成 {scale} 规模增强数据...")
    print(f"📊 增强数据规模配置:")
    for key, value in config.items():
        print(f"   {key}: {value:,}")
    print("-" * 80)
    
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
    print(f"   ✅ 生成 {len(students):,} 名学生，{len(teachers):,} 名教师")
    
    print("\n📖 生成课程数据...")
    courses = course_gen.generate_courses(config['courses'], departments, teachers)
    print(f"   ✅ 生成 {len(courses):,} 门课程")
    
    print("\n🏢 生成设施数据...")
    classrooms = facility_gen.generate_classrooms(config['classrooms'])
    time_slots = facility_gen.generate_time_slots()
    print(f"   ✅ 生成 {len(classrooms)} 间教室，{len(time_slots)} 个时间段")
    
    print("\n🎯 生成复杂场景数据...")
    
    # 分批生成选课记录以避免内存问题
    print("   📝 分批生成选课记录...")
    batch_size = 5000
    student_batches = [students[i:i+batch_size] for i in range(0, len(students), batch_size)]
    enrollments = []
    
    for i, student_batch in enumerate(student_batches):
        print(f"      批次 {i+1}/{len(student_batches)}: {len(student_batch)} 名学生")
        batch_enrollments = scenario_gen.generate_enrollment_data(student_batch, courses)
        enrollments.extend(batch_enrollments)
    
    teacher_preferences = scenario_gen.generate_teacher_preferences(teachers, time_slots)
    print(f"   ✅ 生成 {len(enrollments):,} 条选课记录，{len(teacher_preferences):,} 条教师偏好")
    
    conflicts = []
    constraints = []
    if include_conflicts:
        print("   🔍 生成冲突场景和约束条件...")
        conflicts = scenario_gen.generate_conflict_scenarios(courses, teachers, classrooms, students[:1000])  # 限制学生数量避免性能问题
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

    generation_time = time.time() - start_time
    
    # 添加元数据
    dataset['metadata'] = {
        'scale': scale,
        'generated_at': datetime.now().isoformat(),
        'generator_version': '2.0.0',  # 增强版本
        'config': config,
        'total_records': total_records,
        'generation_time_seconds': round(generation_time, 2),
        'validation_passed': False,  # 将在验证后更新
        'output_formats': output_formats,
        'include_conflicts': include_conflicts
    }
    
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
    print("-" * 80)
    
    return dataset

def main():
    """主函数"""
    print("🚀 开始增强规模数据生成")
    print("="*80)
    
    # 生成huge规模数据（约20-25万条记录）
    try:
        dataset = generate_enhanced_dataset(
            scale='huge',
            output_formats=['json', 'sql'],
            output_dir='enhanced_huge_output',
            validate_data=True,
            include_conflicts=True
        )
        
        print("✅ 数据生成任务完成！")
        metadata = dataset.get('metadata', {})
        print(f"📊 总记录数: {metadata.get('total_records', 0):,}")
        print(f"⏱️ 总耗时: {metadata.get('generation_time_seconds', 0):.2f} 秒")
        print(f"✅ 验证状态: {metadata.get('validation_passed', False)}")
        return True
        
    except Exception as e:
        print(f"❌ 数据生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 增强规模数据生成成功完成")
    else:
        print("❌ 数据生成任务失败")
        sys.exit(1)