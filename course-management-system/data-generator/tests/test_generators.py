# file: data-generator/tests/test_generators.py
# 功能: 生成器功能测试

import unittest
import sys
from pathlib import Path

# 添加父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from generators import (
    DepartmentGenerator,
    UserGenerator,
    CourseGenerator,
    FacilityGenerator,
    ComplexScenarioGenerator,
    DataExporter
)


class TestDepartmentGenerator(unittest.TestCase):
    """院系专业生成器测试"""
    
    def setUp(self):
        self.generator = DepartmentGenerator()
    
    def test_generate_departments(self):
        """测试院系生成"""
        departments = self.generator.generate_departments(5)
        
        self.assertEqual(len(departments), 5)
        
        for dept in departments:
            self.assertIn('id', dept)
            self.assertIn('name', dept)
            self.assertIn('code', dept)
            self.assertIn('dean', dept)
            self.assertIsInstance(dept['id'], int)
            self.assertIsInstance(dept['name'], str)
            self.assertTrue(dept['name'])  # 非空字符串
    
    def test_generate_majors(self):
        """测试专业生成"""
        departments = self.generator.generate_departments(3)
        majors = self.generator.generate_majors(departments)
        
        self.assertGreater(len(majors), 0)
        
        for major in majors:
            self.assertIn('id', major)
            self.assertIn('name', major)
            self.assertIn('department_id', major)
            self.assertIn('degree_type', major)
            
            # 验证外键关系
            dept_ids = [d['id'] for d in departments]
            self.assertIn(major['department_id'], dept_ids)
    
    def test_department_uniqueness(self):
        """测试院系ID唯一性"""
        departments = self.generator.generate_departments(10)
        ids = [dept['id'] for dept in departments]
        self.assertEqual(len(ids), len(set(ids)))  # 无重复ID


class TestUserGenerator(unittest.TestCase):
    """用户生成器测试"""
    
    def setUp(self):
        self.generator = UserGenerator()
        # 创建测试用的院系和专业数据
        dept_gen = DepartmentGenerator()
        self.departments = dept_gen.generate_departments(3)
        self.majors = dept_gen.generate_majors(self.departments)
    
    def test_generate_students(self):
        """测试学生生成"""
        students = self.generator.generate_students(10, self.majors)
        
        self.assertEqual(len(students), 10)
        
        for student in students:
            self.assertIn('id', student)
            self.assertIn('name', student)
            self.assertIn('student_id', student)
            self.assertIn('major_id', student)
            self.assertIn('gender', student)
            
            # 验证性别值
            self.assertIn(student['gender'], ['男', '女'])
            
            # 验证专业ID有效性
            major_ids = [m['id'] for m in self.majors]
            self.assertIn(student['major_id'], major_ids)
    
    def test_generate_teachers(self):
        """测试教师生成"""
        teachers = self.generator.generate_teachers(5, self.departments)
        
        self.assertEqual(len(teachers), 5)
        
        for teacher in teachers:
            self.assertIn('id', teacher)
            self.assertIn('name', teacher)
            self.assertIn('employee_id', teacher)
            self.assertIn('department_id', teacher)
            self.assertIn('title', teacher)
            
            # 验证职称
            self.assertIn(teacher['title'], ['教授', '副教授', '讲师', '助教'])
            
            # 验证院系ID有效性
            dept_ids = [d['id'] for d in self.departments]
            self.assertIn(teacher['department_id'], dept_ids)
    
    def test_chinese_name_generation(self):
        """测试中文姓名生成"""
        for _ in range(10):
            name = self.generator.generate_chinese_name()
            self.assertIsInstance(name, str)
            self.assertGreaterEqual(len(name), 2)
            self.assertLessEqual(len(name), 4)


class TestCourseGenerator(unittest.TestCase):
    """课程生成器测试"""
    
    def setUp(self):
        self.generator = CourseGenerator()
        # 创建测试数据
        dept_gen = DepartmentGenerator()
        user_gen = UserGenerator()
        self.departments = dept_gen.generate_departments(2)
        self.teachers = user_gen.generate_teachers(5, self.departments)
    
    def test_generate_courses(self):
        """测试课程生成"""
        courses = self.generator.generate_courses(8, self.departments, self.teachers)
        
        self.assertEqual(len(courses), 8)
        
        for course in courses:
            self.assertIn('id', course)
            self.assertIn('name', course)
            self.assertIn('code', course)
            self.assertIn('credits', course)
            self.assertIn('department_id', course)
            self.assertIn('teacher_ids', course)
            
            # 验证学分范围
            self.assertGreaterEqual(course['credits'], 1)
            self.assertLessEqual(course['credits'], 5)
            
            # 验证教师ID有效性
            teacher_ids = [t['id'] for t in self.teachers]
            for tid in course['teacher_ids']:
                self.assertIn(tid, teacher_ids)
    
    def test_prerequisite_relationships(self):
        """测试先修课程关系"""
        courses = self.generator.generate_courses(10, self.departments, self.teachers)
        
        for course in courses:
            prerequisites = course.get('prerequisites', [])
            if prerequisites:
                # 先修课程ID应该存在于课程列表中
                course_ids = [c['id'] for c in courses]
                for prereq_id in prerequisites:
                    self.assertIn(prereq_id, course_ids)


class TestFacilityGenerator(unittest.TestCase):
    """设施生成器测试"""
    
    def setUp(self):
        self.generator = FacilityGenerator()
    
    def test_generate_classrooms(self):
        """测试教室生成"""
        classrooms = self.generator.generate_classrooms(6)
        
        self.assertEqual(len(classrooms), 6)
        
        for classroom in classrooms:
            self.assertIn('id', classroom)
            self.assertIn('building', classroom)
            self.assertIn('room_number', classroom)
            self.assertIn('capacity', classroom)
            self.assertIn('room_type', classroom)
            
            # 验证容量为正数
            self.assertGreater(classroom['capacity'], 0)
            
            # 验证教室类型
            valid_types = ['普通教室', '多媒体教室', '实验室', '机房', '阶梯教室', '研讨室']
            self.assertIn(classroom['room_type'], valid_types)
    
    def test_generate_time_slots(self):
        """测试时间段生成"""
        time_slots = self.generator.generate_time_slots()
        
        self.assertGreater(len(time_slots), 0)
        
        for slot in time_slots:
            self.assertIn('id', slot)
            self.assertIn('name', slot)
            self.assertIn('start_time', slot)
            self.assertIn('end_time', slot)
            self.assertIn('duration', slot)
            
            # 验证时间格式
            self.assertRegex(slot['start_time'], r'^\d{2}:\d{2}$')
            self.assertRegex(slot['end_time'], r'^\d{2}:\d{2}$')


class TestComplexScenarioGenerator(unittest.TestCase):
    """复杂场景生成器测试"""
    
    def setUp(self):
        self.generator = ComplexScenarioGenerator()
        # 创建测试数据
        dept_gen = DepartmentGenerator()
        user_gen = UserGenerator()
        course_gen = CourseGenerator()
        facility_gen = FacilityGenerator()
        
        self.departments = dept_gen.generate_departments(2)
        self.majors = dept_gen.generate_majors(self.departments)
        self.students = user_gen.generate_students(20, self.majors)
        self.teachers = user_gen.generate_teachers(5, self.departments)
        self.courses = course_gen.generate_courses(10, self.departments, self.teachers)
        self.classrooms = facility_gen.generate_classrooms(5)
        self.time_slots = facility_gen.generate_time_slots()
    
    def test_generate_enrollment_data(self):
        """测试选课数据生成"""
        enrollments = self.generator.generate_enrollment_data(self.students, self.courses)
        
        self.assertGreater(len(enrollments), 0)
        
        for enrollment in enrollments:
            self.assertIn('student_id', enrollment)
            self.assertIn('course_id', enrollment)
            self.assertIn('status', enrollment)
            
            # 验证外键关系
            student_ids = [s['id'] for s in self.students]
            course_ids = [c['id'] for c in self.courses]
            self.assertIn(enrollment['student_id'], student_ids)
            self.assertIn(enrollment['course_id'], course_ids)
    
    def test_generate_teacher_preferences(self):
        """测试教师偏好生成"""
        preferences = self.generator.generate_teacher_preferences(self.teachers, self.time_slots)
        
        self.assertGreater(len(preferences), 0)
        
        for pref in preferences:
            self.assertIn('teacher_id', pref)
            self.assertIn('time_slot_id', pref)
            self.assertIn('preference_score', pref)
            
            # 验证偏好分数范围
            self.assertGreaterEqual(pref['preference_score'], 0.0)
            self.assertLessEqual(pref['preference_score'], 1.0)
    
    def test_generate_conflict_scenarios(self):
        """测试冲突场景生成"""
        conflicts = self.generator.generate_conflict_scenarios(
            self.courses, self.teachers, self.classrooms, self.students
        )
        
        # 冲突数量可能为0，这是正常的
        for conflict in conflicts:
            self.assertIn('type', conflict)
            self.assertIn('severity', conflict)
            self.assertIn('description', conflict)


class TestDataExporter(unittest.TestCase):
    """数据导出器测试"""
    
    def setUp(self):
        self.exporter = DataExporter('test_output')
        # 创建简单的测试数据
        self.test_data = {
            'departments': [
                {'id': 1, 'name': '测试院系', 'code': 'TEST001'},
                {'id': 2, 'name': '示例院系', 'code': 'DEMO001'}
            ],
            'majors': [
                {'id': 1, 'name': '测试专业', 'department_id': 1},
                {'id': 2, 'name': '示例专业', 'department_id': 2}
            ]
        }
    
    def test_validate_data_integrity(self):
        """测试数据完整性验证"""
        errors = self.exporter.validate_data_integrity(self.test_data)
        
        # 测试数据应该没有错误
        self.assertIsInstance(errors, dict)
    
    def test_validate_foreign_keys(self):
        """测试外键验证"""
        # 创建有外键错误的数据
        bad_data = {
            'departments': [{'id': 1, 'name': '院系1', 'code': 'DEPT1'}],
            'majors': [{'id': 1, 'name': '专业1', 'department_id': 999}]  # 不存在的院系ID
        }
        
        errors = self.exporter.validate_data_integrity(bad_data)
        self.assertIn('majors', errors)


if __name__ == '__main__':
    unittest.main()
