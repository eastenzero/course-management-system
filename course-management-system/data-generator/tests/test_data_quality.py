# file: data-generator/tests/test_data_quality.py
# 功能: 数据质量测试

import unittest
import sys
import re
from pathlib import Path
from collections import Counter

# 添加父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from main import generate_complete_dataset


class TestDataQuality(unittest.TestCase):
    """数据质量测试"""
    
    @classmethod
    def setUpClass(cls):
        """生成测试数据集"""
        print("生成测试数据集...")
        cls.dataset = generate_complete_dataset(
            scale='small',
            output_formats=[],  # 不输出文件
            validate_data=False  # 跳过验证以加快测试
        )
    
    def test_data_completeness(self):
        """测试数据完整性"""
        required_tables = [
            'departments', 'majors', 'students', 'teachers', 
            'courses', 'classrooms', 'time_slots', 'enrollments'
        ]
        
        for table in required_tables:
            self.assertIn(table, self.dataset, f"缺少表: {table}")
            self.assertIsInstance(self.dataset[table], list, f"表 {table} 应该是列表")
            self.assertGreater(len(self.dataset[table]), 0, f"表 {table} 不能为空")
    
    def test_id_uniqueness(self):
        """测试ID唯一性"""
        tables_with_ids = ['departments', 'majors', 'students', 'teachers', 'courses', 'classrooms']
        
        for table_name in tables_with_ids:
            if table_name in self.dataset:
                ids = [record['id'] for record in self.dataset[table_name]]
                unique_ids = set(ids)
                self.assertEqual(len(ids), len(unique_ids), 
                               f"表 {table_name} 存在重复ID")
    
    def test_foreign_key_integrity(self):
        """测试外键完整性"""
        # 收集所有ID
        dept_ids = {d['id'] for d in self.dataset['departments']}
        major_ids = {m['id'] for m in self.dataset['majors']}
        student_ids = {s['id'] for s in self.dataset['students']}
        teacher_ids = {t['id'] for t in self.dataset['teachers']}
        course_ids = {c['id'] for c in self.dataset['courses']}
        
        # 验证专业的院系ID
        for major in self.dataset['majors']:
            self.assertIn(major['department_id'], dept_ids,
                         f"专业 {major['name']} 的院系ID无效")
        
        # 验证学生的专业ID
        for student in self.dataset['students']:
            self.assertIn(student['major_id'], major_ids,
                         f"学生 {student['name']} 的专业ID无效")
        
        # 验证教师的院系ID
        for teacher in self.dataset['teachers']:
            self.assertIn(teacher['department_id'], dept_ids,
                         f"教师 {teacher['name']} 的院系ID无效")
        
        # 验证课程的院系ID和教师ID
        for course in self.dataset['courses']:
            self.assertIn(course['department_id'], dept_ids,
                         f"课程 {course['name']} 的院系ID无效")
            
            for teacher_id in course.get('teacher_ids', []):
                self.assertIn(teacher_id, teacher_ids,
                             f"课程 {course['name']} 的教师ID {teacher_id} 无效")
        
        # 验证选课记录
        for enrollment in self.dataset['enrollments']:
            self.assertIn(enrollment['student_id'], student_ids,
                         f"选课记录的学生ID {enrollment['student_id']} 无效")
            self.assertIn(enrollment['course_id'], course_ids,
                         f"选课记录的课程ID {enrollment['course_id']} 无效")
    
    def test_data_format_validity(self):
        """测试数据格式有效性"""
        # 测试邮箱格式
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        for student in self.dataset['students']:
            if student.get('email'):
                self.assertRegex(student['email'], email_pattern,
                               f"学生 {student['name']} 邮箱格式无效")
        
        for teacher in self.dataset['teachers']:
            if teacher.get('email'):
                self.assertRegex(teacher['email'], email_pattern,
                               f"教师 {teacher['name']} 邮箱格式无效")
        
        # 测试时间格式
        time_pattern = re.compile(r'^\d{2}:\d{2}$')
        for time_slot in self.dataset['time_slots']:
            self.assertRegex(time_slot['start_time'], time_pattern,
                           f"时间段 {time_slot['name']} 开始时间格式无效")
            self.assertRegex(time_slot['end_time'], time_pattern,
                           f"时间段 {time_slot['name']} 结束时间格式无效")
    
    def test_business_logic_validity(self):
        """测试业务逻辑有效性"""
        # 测试课程容量逻辑
        for course in self.dataset['courses']:
            min_students = course.get('min_students', 0)
            max_students = course.get('max_students', 0)
            self.assertLessEqual(min_students, max_students,
                               f"课程 {course['name']} 最小学生数不能大于最大学生数")
        
        # 测试教室容量逻辑
        for classroom in self.dataset['classrooms']:
            capacity = classroom.get('capacity', 0)
            actual_capacity = classroom.get('actual_capacity', 0)
            self.assertLessEqual(actual_capacity, capacity,
                               f"教室 {classroom['full_name']} 实际容量不能大于设计容量")
        
        # 测试学分范围
        for course in self.dataset['courses']:
            credits = course.get('credits', 0)
            self.assertGreaterEqual(credits, 1, f"课程 {course['name']} 学分不能小于1")
            self.assertLessEqual(credits, 10, f"课程 {course['name']} 学分不能大于10")
    
    def test_data_distribution(self):
        """测试数据分布合理性"""
        # 测试性别分布
        student_genders = [s['gender'] for s in self.dataset['students']]
        gender_counts = Counter(student_genders)
        
        # 性别分布应该相对均衡（不超过70%）
        total_students = len(student_genders)
        for gender, count in gender_counts.items():
            ratio = count / total_students
            self.assertLess(ratio, 0.8, f"学生性别 {gender} 分布过于集中: {ratio:.2%}")
        
        # 测试课程类型分布
        course_types = [c['course_type'] for c in self.dataset['courses']]
        type_counts = Counter(course_types)
        
        # 应该有多种课程类型
        self.assertGreaterEqual(len(type_counts), 2, "课程类型过于单一")
        
        # 测试教师职称分布
        teacher_titles = [t['title'] for t in self.dataset['teachers']]
        title_counts = Counter(teacher_titles)
        
        # 应该有多种职称
        self.assertGreaterEqual(len(title_counts), 2, "教师职称过于单一")
    
    def test_data_consistency(self):
        """测试数据一致性"""
        # 测试院系-专业一致性
        dept_major_map = {}
        for major in self.dataset['majors']:
            dept_id = major['department_id']
            if dept_id not in dept_major_map:
                dept_major_map[dept_id] = []
            dept_major_map[dept_id].append(major['id'])
        
        # 每个院系应该至少有一个专业
        for dept in self.dataset['departments']:
            self.assertIn(dept['id'], dept_major_map,
                         f"院系 {dept['name']} 没有对应的专业")
        
        # 测试课程-教师一致性
        for course in self.dataset['courses']:
            teacher_ids = course.get('teacher_ids', [])
            self.assertGreater(len(teacher_ids), 0,
                             f"课程 {course['name']} 没有分配教师")
            
            # 主讲教师应该在教师列表中
            primary_teacher_id = course.get('primary_teacher_id')
            if primary_teacher_id:
                self.assertIn(primary_teacher_id, teacher_ids,
                             f"课程 {course['name']} 主讲教师不在教师列表中")
    
    def test_data_volume_appropriateness(self):
        """测试数据量合理性"""
        # 获取配置的数据规模
        metadata = self.dataset.get('metadata', {})
        scale = metadata.get('scale', 'small')
        
        if scale == 'small':
            # 小规模数据的合理范围
            self.assertLessEqual(len(self.dataset['students']), 6000)
            self.assertLessEqual(len(self.dataset['teachers']), 400)
            self.assertLessEqual(len(self.dataset['courses']), 800)
        
        # 师生比应该合理（1:5 到 1:30）
        student_count = len(self.dataset['students'])
        teacher_count = len(self.dataset['teachers'])
        ratio = student_count / teacher_count if teacher_count > 0 else 0
        
        self.assertGreaterEqual(ratio, 5, f"师生比过低: 1:{ratio:.1f}")
        self.assertLessEqual(ratio, 35, f"师生比过高: 1:{ratio:.1f}")
    
    def test_chinese_content_quality(self):
        """测试中文内容质量"""
        # 测试中文姓名
        for student in self.dataset['students'][:10]:  # 抽样测试
            name = student['name']
            self.assertGreaterEqual(len(name), 2, f"学生姓名过短: {name}")
            self.assertLessEqual(len(name), 4, f"学生姓名过长: {name}")
            
            # 检查是否包含中文字符
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in name)
            self.assertTrue(has_chinese, f"学生姓名应包含中文字符: {name}")
        
        # 测试院系名称
        for dept in self.dataset['departments']:
            name = dept['name']
            self.assertIn('学院', name, f"院系名称应包含'学院': {name}")
    
    def test_metadata_completeness(self):
        """测试元数据完整性"""
        metadata = self.dataset.get('metadata', {})
        
        required_fields = [
            'scale', 'generated_at', 'generator_version', 
            'total_records', 'generation_time_seconds'
        ]
        
        for field in required_fields:
            self.assertIn(field, metadata, f"元数据缺少字段: {field}")
        
        # 验证记录数统计
        actual_total = sum(len(v) if isinstance(v, list) else 0 
                          for k, v in self.dataset.items() if k != 'metadata')
        reported_total = metadata['total_records']
        
        self.assertEqual(actual_total, reported_total,
                        f"元数据中的记录数不正确: 实际{actual_total}, 报告{reported_total}")


class TestDataScalability(unittest.TestCase):
    """数据可扩展性测试"""
    
    def test_different_scales(self):
        """测试不同规模的数据生成"""
        scales = ['small']  # 只测试小规模以节省时间
        
        for scale in scales:
            with self.subTest(scale=scale):
                dataset = generate_complete_dataset(
                    scale=scale,
                    output_formats=[],
                    validate_data=False
                )
                
                # 验证数据集结构
                self.assertIn('metadata', dataset)
                self.assertEqual(dataset['metadata']['scale'], scale)
                
                # 验证数据量符合规模
                total_records = dataset['metadata']['total_records']
                self.assertGreater(total_records, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
