# file: data-generator/generators/exporter.py
# 功能: 数据导出和验证器

import json
import os
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, date
from pathlib import Path
from faker import Faker

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OUTPUT_CONFIG, VALIDATION_CONFIG


class DataExporter:
    """数据导出器
    
    负责数据导出和验证，包括：
    - JSON格式导出
    - SQL格式导出
    - 数据完整性验证
    - 数据质量报告生成
    """
    
    def __init__(self, output_dir: str = 'output'):
        """初始化导出器
        
        Args:
            output_dir: 输出目录
        """
        self.fake = Faker('zh_CN')
        self.output_dir = Path(output_dir)
        self.json_dir = self.output_dir / 'json'
        self.sql_dir = self.output_dir / 'sql'
        self.reports_dir = self.output_dir / 'reports'
        
        # 创建输出目录
        self._create_directories()
        
        # SQL表结构映射
        self.table_schemas = {
            'departments': [
                'id', 'name', 'code', 'dean', 'dean_title', 'phone', 'email',
                'office_address', 'building_location', 'established_year', 'staff_count',
                'student_count', 'description', 'website', 'budget', 'is_active',
                'created_at', 'updated_at'
            ],
            'majors': [
                'id', 'name', 'code', 'english_name', 'department_id', 'degree_type',
                'duration', 'total_credits', 'tuition_fee', 'enrollment_quota',
                'current_students', 'employment_rate', 'description', 'is_active',
                'accreditation', 'ranking', 'created_at', 'updated_at'
            ],
            'students': [
                'id', 'student_id', 'username', 'password_hash', 'name', 'gender',
                'birth_date', 'id_card', 'phone', 'email', 'personal_email',
                'major_id', 'grade', 'class_number', 'student_type', 'enrollment_status',
                'academic_status', 'gpa', 'total_credits', 'completed_credits',
                'home_address', 'emergency_contact', 'emergency_phone', 'emergency_relationship',
                'political_status', 'ethnicity', 'health_status', 'is_active',
                'last_login', 'created_at', 'updated_at'
            ],
            'teachers': [
                'id', 'employee_id', 'username', 'password_hash', 'name', 'gender',
                'birth_date', 'id_card', 'phone', 'email', 'personal_email',
                'department_id', 'title', 'degree', 'graduation_school', 'major_field',
                'hire_date', 'employment_type', 'employment_status', 'office_location',
                'office_phone', 'max_weekly_hours', 'salary_level', 'home_address',
                'marital_status', 'political_status', 'is_active', 'last_login',
                'created_at', 'updated_at'
            ],
            'courses': [
                'id', 'code', 'name', 'english_name', 'department_id', 'credits',
                'theory_hours', 'practice_hours', 'total_hours', 'course_type',
                'semester', 'max_students', 'min_students', 'current_enrolled',
                'description', 'assessment_method', 'textbook', 'language',
                'difficulty_level', 'primary_teacher_id', 'is_active', 'is_elective',
                'selection_priority', 'withdrawal_deadline', 'final_exam_type',
                'attendance_requirement', 'homework_frequency', 'lab_required',
                'field_trip', 'created_at', 'updated_at'
            ],
            'classrooms': [
                'id', 'building', 'floor', 'room_number', 'full_name', 'room_type',
                'capacity', 'actual_capacity', 'area', 'is_available', 'availability_reason',
                'maintenance_status', 'last_maintenance', 'next_maintenance',
                'hourly_rate', 'security_level', 'manager', 'manager_phone',
                'manager_email', 'emergency_contact', 'location_description',
                'utilization_rate', 'qr_code', 'is_smart_classroom', 'energy_efficiency',
                'wifi_ssid', 'wifi_password', 'created_at', 'updated_at'
            ],
            'time_slots': [
                'id', 'name', 'start_time', 'end_time', 'duration', 'break_time',
                'period', 'is_active', 'is_prime_time', 'order', 'day_sequence',
                'exam_period', 'popularity_score', 'conflict_probability',
                'teacher_preference', 'student_preference', 'energy_cost',
                'description', 'created_at', 'updated_at'
            ],
            'enrollments': [
                'id', 'student_id', 'course_id', 'semester', 'academic_year',
                'enrollment_type', 'status', 'priority', 'selection_time',
                'grade', 'attendance_rate', 'midterm_score', 'final_score',
                'total_score', 'gpa_points', 'is_retake', 'retake_count',
                'withdrawal_reason', 'special_notes', 'created_at', 'updated_at'
            ],
            'teacher_preferences': [
                'id', 'teacher_id', 'day_of_week', 'time_slot_id', 'preference_score',
                'preference_level', 'reason', 'is_available', 'max_courses',
                'avoid_back_to_back', 'travel_time_needed', 'flexibility',
                'created_at', 'updated_at'
            ],
            'conflicts': [
                'id', 'type', 'severity', 'description', 'impact_score',
                'suggested_solution', 'created_at'
            ]
        }
    
    def export_to_json(self, data_dict: Dict[str, Any], filename: str = None) -> str:
        """导出为JSON格式
        
        Args:
            data_dict: 要导出的数据字典
            filename: 文件名，如果为None则自动生成
            
        Returns:
            导出文件的路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"course_data_{timestamp}.json"
        
        filepath = self.json_dir / filename
        
        # 处理日期时间序列化
        def json_serializer(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(filepath, 'w', encoding=OUTPUT_CONFIG['encoding']) as f:
            json.dump(data_dict, f, ensure_ascii=False, 
                     indent=OUTPUT_CONFIG['indent'], default=json_serializer)
        
        print(f"JSON数据已导出到: {filepath}")
        return str(filepath)
    
    def export_to_sql(self, data_dict: Dict[str, Any], filename: str = None) -> str:
        """导出为SQL格式
        
        Args:
            data_dict: 要导出的数据字典
            filename: 文件名，如果为None则自动生成
            
        Returns:
            导出文件的路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"course_data_{timestamp}.sql"
        
        filepath = self.sql_dir / filename
        
        with open(filepath, 'w', encoding=OUTPUT_CONFIG['encoding']) as f:
            f.write("-- 校园课程表管理系统测试数据\n")
            f.write(f"-- 生成时间: {datetime.now()}\n")
            f.write("-- 编码: UTF-8\n\n")
            
            f.write("SET NAMES utf8mb4;\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
            
            # 按依赖顺序导出表
            table_order = [
                'departments', 'majors', 'students', 'teachers', 'courses',
                'classrooms', 'time_slots', 'enrollments', 'teacher_preferences', 'conflicts'
            ]
            
            for table_name in table_order:
                if table_name in data_dict and data_dict[table_name]:
                    f.write(f"-- {table_name} 表数据\n")
                    self._write_insert_statements(f, table_name, data_dict[table_name])
                    f.write("\n")
            
            f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
        
        print(f"SQL数据已导出到: {filepath}")
        return str(filepath)
    
    def validate_data_integrity(self, data_dict: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证数据完整性
        
        Args:
            data_dict: 要验证的数据字典
            
        Returns:
            验证错误字典
        """
        errors = {}
        
        # 验证必需字段
        errors.update(self._validate_required_fields(data_dict))
        
        # 验证外键关系
        errors.update(self._validate_foreign_keys(data_dict))
        
        # 验证数据类型
        errors.update(self._validate_data_types(data_dict))
        
        # 验证业务逻辑
        errors.update(self._validate_business_logic(data_dict))
        
        return errors
    
    def generate_data_report(self, data_dict: Dict[str, Any], 
                           validation_errors: Dict[str, List[str]] = None) -> str:
        """生成数据质量报告
        
        Args:
            data_dict: 数据字典
            validation_errors: 验证错误
            
        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f"data_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 数据生成报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 数据统计
            f.write("## 数据统计\n\n")
            total_records = 0
            for table_name, records in data_dict.items():
                if isinstance(records, list):
                    count = len(records)
                    total_records += count
                    f.write(f"- **{table_name}**: {count:,} 条记录\n")
            
            f.write(f"\n**总计**: {total_records:,} 条记录\n\n")
            
            # 数据质量
            f.write("## 数据质量\n\n")
            if validation_errors:
                f.write("### 发现的问题\n\n")
                for table_name, error_list in validation_errors.items():
                    if error_list:
                        f.write(f"#### {table_name}\n\n")
                        for error in error_list[:10]:  # 只显示前10个错误
                            f.write(f"- {error}\n")
                        if len(error_list) > 10:
                            f.write(f"- ... 还有 {len(error_list) - 10} 个错误\n")
                        f.write("\n")
            else:
                f.write("✅ 数据验证通过，未发现问题\n\n")
            
            # 数据特征
            f.write("## 数据特征\n\n")
            self._write_data_characteristics(f, data_dict)
            
            # 建议
            f.write("## 建议\n\n")
            self._write_recommendations(f, data_dict, validation_errors)
        
        print(f"数据报告已生成: {report_file}")
        return str(report_file)

    def _create_directories(self) -> None:
        """创建输出目录"""
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.sql_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _write_insert_statements(self, file, table_name: str, records: List[Dict[str, Any]]) -> None:
        """写入SQL插入语句"""
        if not records:
            return

        # 获取表结构
        columns = self.table_schemas.get(table_name, list(records[0].keys()))

        # 写入表结构注释
        file.write(f"-- 表: {table_name}\n")
        file.write(f"-- 记录数: {len(records)}\n")

        # 分批插入，每批1000条记录
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            file.write(f"INSERT INTO `{table_name}` (")
            file.write(", ".join([f"`{col}`" for col in columns]))
            file.write(") VALUES\n")

            for j, record in enumerate(batch):
                values = []
                for col in columns:
                    value = record.get(col)
                    if value is None:
                        values.append("NULL")
                    elif isinstance(value, str):
                        # 转义单引号
                        escaped_value = value.replace("'", "''")
                        values.append(f"'{escaped_value}'")
                    elif isinstance(value, (datetime, date)):
                        values.append(f"'{value.isoformat()}'")
                    elif isinstance(value, bool):
                        values.append("1" if value else "0")
                    elif isinstance(value, (list, dict)):
                        # 将复杂对象转换为JSON字符串
                        json_str = json.dumps(value, ensure_ascii=False, default=str)
                        escaped_json = json_str.replace("'", "''")
                        values.append(f"'{escaped_json}'")
                    else:
                        values.append(str(value))

                file.write(f"({', '.join(values)})")
                if j < len(batch) - 1:
                    file.write(",\n")
                else:
                    file.write(";\n\n")

    def _validate_required_fields(self, data_dict: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证必需字段"""
        errors = {}

        for table_name, required_fields in VALIDATION_CONFIG['required_fields'].items():
            if table_name not in data_dict:
                continue

            records = data_dict[table_name]
            if not isinstance(records, list):
                continue

            table_errors = []
            for i, record in enumerate(records):
                for field in required_fields:
                    if field not in record or record[field] is None:
                        table_errors.append(f"记录 {i+1}: 缺少必需字段 '{field}'")

                        # 限制错误数量
                        if len(table_errors) >= VALIDATION_CONFIG['max_errors_per_type']:
                            table_errors.append("... 错误过多，已截断")
                            break

                if len(table_errors) >= VALIDATION_CONFIG['max_errors_per_type']:
                    break

            if table_errors:
                errors[table_name] = table_errors

        return errors

    def _validate_foreign_keys(self, data_dict: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证外键关系"""
        errors = {}

        # 构建ID集合
        department_ids = set()
        major_ids = set()
        student_ids = set()
        teacher_ids = set()
        course_ids = set()
        classroom_ids = set()
        time_slot_ids = set()

        if 'departments' in data_dict:
            department_ids = {d['id'] for d in data_dict['departments']}
        if 'majors' in data_dict:
            major_ids = {m['id'] for m in data_dict['majors']}
        if 'students' in data_dict:
            student_ids = {s['id'] for s in data_dict['students']}
        if 'teachers' in data_dict:
            teacher_ids = {t['id'] for t in data_dict['teachers']}
        if 'courses' in data_dict:
            course_ids = {c['id'] for c in data_dict['courses']}
        if 'classrooms' in data_dict:
            classroom_ids = {c['id'] for c in data_dict['classrooms']}
        if 'time_slots' in data_dict:
            time_slot_ids = {t['id'] for t in data_dict['time_slots']}

        # 验证专业的院系ID
        if 'majors' in data_dict:
            major_errors = []
            for major in data_dict['majors']:
                if major.get('department_id') not in department_ids:
                    major_errors.append(f"专业 '{major.get('name')}' 的院系ID {major.get('department_id')} 不存在")
            if major_errors:
                errors['majors'] = major_errors

        # 验证学生的专业ID
        if 'students' in data_dict:
            student_errors = []
            for student in data_dict['students']:
                if student.get('major_id') not in major_ids:
                    student_errors.append(f"学生 '{student.get('name')}' 的专业ID {student.get('major_id')} 不存在")
            if student_errors:
                errors['students'] = student_errors

        # 验证教师的院系ID
        if 'teachers' in data_dict:
            teacher_errors = []
            for teacher in data_dict['teachers']:
                if teacher.get('department_id') not in department_ids:
                    teacher_errors.append(f"教师 '{teacher.get('name')}' 的院系ID {teacher.get('department_id')} 不存在")
            if teacher_errors:
                errors['teachers'] = teacher_errors

        # 验证课程的院系ID和教师ID
        if 'courses' in data_dict:
            course_errors = []
            for course in data_dict['courses']:
                if course.get('department_id') not in department_ids:
                    course_errors.append(f"课程 '{course.get('name')}' 的院系ID {course.get('department_id')} 不存在")

                if course.get('primary_teacher_id') not in teacher_ids:
                    course_errors.append(f"课程 '{course.get('name')}' 的主讲教师ID {course.get('primary_teacher_id')} 不存在")

            if course_errors:
                errors['courses'] = course_errors

        return errors

    def _validate_data_types(self, data_dict: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证数据类型"""
        errors = {}

        # 这里可以添加具体的数据类型验证逻辑
        # 例如：验证邮箱格式、电话号码格式、日期格式等

        return errors

    def _validate_business_logic(self, data_dict: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证业务逻辑"""
        errors = {}

        # 验证课程容量
        if 'courses' in data_dict:
            course_errors = []
            for course in data_dict['courses']:
                if course.get('min_students', 0) > course.get('max_students', 0):
                    course_errors.append(f"课程 '{course.get('name')}' 最小学生数大于最大学生数")

            if course_errors:
                errors['courses'] = course_errors

        # 验证教室容量
        if 'classrooms' in data_dict:
            classroom_errors = []
            for classroom in data_dict['classrooms']:
                if classroom.get('actual_capacity', 0) > classroom.get('capacity', 0):
                    classroom_errors.append(f"教室 '{classroom.get('full_name')}' 实际容量大于设计容量")

            if classroom_errors:
                errors['classrooms'] = classroom_errors

        return errors

    def _write_data_characteristics(self, file, data_dict: Dict[str, Any]) -> None:
        """写入数据特征分析"""
        # 院系分布
        if 'departments' in data_dict:
            file.write("### 院系分布\n\n")
            dept_count = len(data_dict['departments'])
            file.write(f"- 总院系数: {dept_count}\n")

            if 'majors' in data_dict:
                majors_per_dept = len(data_dict['majors']) / dept_count if dept_count > 0 else 0
                file.write(f"- 平均每院系专业数: {majors_per_dept:.1f}\n")

            file.write("\n")

        # 师生比例
        if 'students' in data_dict and 'teachers' in data_dict:
            file.write("### 师生比例\n\n")
            student_count = len(data_dict['students'])
            teacher_count = len(data_dict['teachers'])
            ratio = student_count / teacher_count if teacher_count > 0 else 0
            file.write(f"- 学生总数: {student_count:,}\n")
            file.write(f"- 教师总数: {teacher_count:,}\n")
            file.write(f"- 师生比: 1:{ratio:.1f}\n\n")

        # 课程分布
        if 'courses' in data_dict:
            file.write("### 课程分布\n\n")
            courses = data_dict['courses']
            course_types = {}
            for course in courses:
                course_type = course.get('course_type', '未知')
                course_types[course_type] = course_types.get(course_type, 0) + 1

            for course_type, count in course_types.items():
                percentage = count / len(courses) * 100
                file.write(f"- {course_type}: {count} 门 ({percentage:.1f}%)\n")

            file.write("\n")

        # 教室利用率
        if 'classrooms' in data_dict:
            file.write("### 教室分析\n\n")
            classrooms = data_dict['classrooms']
            room_types = {}
            total_capacity = 0

            for classroom in classrooms:
                room_type = classroom.get('room_type', '未知')
                room_types[room_type] = room_types.get(room_type, 0) + 1
                total_capacity += classroom.get('capacity', 0)

            file.write(f"- 教室总数: {len(classrooms)}\n")
            file.write(f"- 总容量: {total_capacity:,} 人\n")
            file.write(f"- 平均容量: {total_capacity / len(classrooms):.1f} 人\n")

            file.write("\n教室类型分布:\n")
            for room_type, count in room_types.items():
                percentage = count / len(classrooms) * 100
                file.write(f"- {room_type}: {count} 间 ({percentage:.1f}%)\n")

            file.write("\n")

    def _write_recommendations(self, file, data_dict: Dict[str, Any],
                             validation_errors: Dict[str, List[str]] = None) -> None:
        """写入建议"""
        recommendations = []

        # 基于数据量的建议
        if 'students' in data_dict and 'teachers' in data_dict:
            student_count = len(data_dict['students'])
            teacher_count = len(data_dict['teachers'])
            ratio = student_count / teacher_count if teacher_count > 0 else 0

            if ratio > 25:
                recommendations.append("师生比过高，建议增加教师数量或减少学生数量")
            elif ratio < 10:
                recommendations.append("师生比较低，资源配置较为充足")

        # 基于课程分布的建议
        if 'courses' in data_dict:
            courses = data_dict['courses']
            elective_count = sum(1 for c in courses if c.get('is_elective', False))
            elective_ratio = elective_count / len(courses) if courses else 0

            if elective_ratio < 0.3:
                recommendations.append("选修课比例较低，建议增加选修课程以提高学生选择性")
            elif elective_ratio > 0.6:
                recommendations.append("选修课比例较高，注意必修课程的覆盖")

        # 基于验证错误的建议
        if validation_errors:
            if any(validation_errors.values()):
                recommendations.append("发现数据完整性问题，建议修复后再使用")
                recommendations.append("可以使用数据清洗工具自动修复部分问题")

        # 基于数据规模的建议
        total_records = sum(len(v) if isinstance(v, list) else 0 for v in data_dict.values())
        if total_records > 100000:
            recommendations.append("数据量较大，建议使用分批处理和索引优化")
            recommendations.append("考虑使用数据库分区来提高查询性能")

        # 排课算法建议
        if 'conflicts' in data_dict and data_dict['conflicts']:
            conflict_count = len(data_dict['conflicts'])
            if conflict_count > 50:
                recommendations.append(f"检测到 {conflict_count} 个潜在冲突，建议优化排课算法参数")
                recommendations.append("可以考虑使用遗传算法或模拟退火算法来解决复杂冲突")

        # 写入建议
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                file.write(f"{i}. {rec}\n")
        else:
            file.write("暂无特殊建议，数据质量良好。\n")

        file.write("\n")
        file.write("---\n")
        file.write("*此报告由数据生成器自动生成*\n")
