# file: data-generator/generators/course.py
# 功能: 课程数据生成器

import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from faker import Faker

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COURSE_CONFIG


class CourseGenerator:
    """课程数据生成器
    
    负责生成课程数据，包括：
    - 课程基本信息
    - 先修课程关系
    - 教师分配
    - 课程安排和要求
    """
    
    def __init__(self, locale: str = 'zh_CN'):
        """初始化生成器
        
        Args:
            locale: 本地化设置，默认为中文
        """
        self.fake = Faker(locale)
        self.course_templates = COURSE_CONFIG['templates']
        self.course_types = COURSE_CONFIG['types']
        self.course_type_weights = COURSE_CONFIG['type_weights']
        self.credit_options = COURSE_CONFIG['credit_options']
        self.credit_weights = COURSE_CONFIG['credit_weights']
        self.assessment_methods = COURSE_CONFIG['assessment_methods']
        
        # 课程名称英文翻译映射
        self.name_translations = {
            "数据结构与算法": "Data Structures and Algorithms",
            "计算机网络": "Computer Networks",
            "操作系统": "Operating Systems",
            "数据库系统": "Database Systems",
            "软件工程": "Software Engineering",
            "编译原理": "Compiler Principles",
            "计算机组成原理": "Computer Organization",
            "人工智能导论": "Introduction to Artificial Intelligence",
            "机器学习": "Machine Learning",
            "深度学习": "Deep Learning",
            "高等数学": "Advanced Mathematics",
            "线性代数": "Linear Algebra",
            "概率论与数理统计": "Probability and Statistics",
            "离散数学": "Discrete Mathematics",
            "大学物理": "College Physics",
            "理论力学": "Theoretical Mechanics",
            "微观经济学": "Microeconomics",
            "宏观经济学": "Macroeconomics",
            "管理学原理": "Principles of Management"
        }
        
        # 设置随机种子
        Faker.seed(42)
        random.seed(42)
    
    def generate_courses(self, count: int, departments: List[Dict[str, Any]], 
                        teachers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成课程数据
        
        Args:
            count: 要生成的课程数量
            departments: 院系数据列表
            teachers: 教师数据列表
            
        Returns:
            课程数据列表
        """
        courses = []
        
        for i in range(count):
            department = random.choice(departments)
            dept_name = department['name']
            
            # 根据院系选择课程类别
            category = self._get_course_category(dept_name)
            course_name = random.choice(self.course_templates[category])
            
            # 为课程分配教师
            dept_teachers = [t for t in teachers if t['department_id'] == department['id']]
            if not dept_teachers:
                # 如果该院系没有教师，从其他院系选择
                dept_teachers = random.sample(teachers, min(3, len(teachers)))
            
            assigned_teachers = random.sample(dept_teachers, random.randint(1, min(3, len(dept_teachers))))
            
            # 生成课程基本信息
            credits = random.choices(self.credit_options, weights=self.credit_weights)[0]
            course_type = random.choices(self.course_types, weights=self.course_type_weights)[0]
            
            course = {
                'id': i + 1,
                'code': f"{department['code']}{i+1:04d}",
                'name': course_name,
                'english_name': self._translate_course_name(course_name),
                'department_id': department['id'],
                'credits': credits,
                'theory_hours': self._calculate_theory_hours(credits),
                'practice_hours': self._calculate_practice_hours(credits, course_name),
                'total_hours': 0,  # 将在后面计算
                'course_type': course_type,
                'semester': self._determine_semester(course_name, course_type),
                'max_students': self._determine_max_students(course_type, course_name),
                'min_students': random.randint(10, 30),
                'current_enrolled': 0,  # 初始为0，选课时更新
                'description': self._generate_course_description(course_name),
                'objectives': self._generate_learning_objectives(course_name),
                'syllabus': self._generate_syllabus(course_name),
                'prerequisites': [],  # 将在后面设置
                'corequisites': [],  # 同修课程
                'assessment_method': random.choice(self.assessment_methods),
                'assessment_breakdown': self._generate_assessment_breakdown(),
                'textbook': self._generate_textbook(course_name),
                'reference_books': self._generate_reference_books(course_name),
                'teaching_methods': self._generate_teaching_methods(),
                'course_website': f"http://course{i+1}.university.edu.cn",
                'language': random.choices(['中文', '英文', '双语'], weights=[0.8, 0.1, 0.1])[0],
                'difficulty_level': self._determine_difficulty_level(course_name),
                'teacher_ids': [t['id'] for t in assigned_teachers],
                'primary_teacher_id': assigned_teachers[0]['id'],
                'classroom_requirements': self._generate_classroom_requirements(course_name),
                'equipment_requirements': self._generate_equipment_requirements(course_name),
                'is_active': random.choices([True, False], weights=[0.95, 0.05])[0],
                'is_elective': course_type in ['选修', '限选'],
                'selection_priority': random.randint(1, 5) if course_type in ['选修', '限选'] else None,
                'withdrawal_deadline': self._generate_withdrawal_deadline(),
                'final_exam_type': random.choices(['闭卷', '开卷', '论文', '项目'], weights=[0.6, 0.2, 0.1, 0.1])[0],
                'attendance_requirement': random.uniform(0.7, 0.9),  # 出勤要求
                'homework_frequency': random.choice(['每周', '每两周', '每月', '不定期']),
                'lab_required': self._has_lab_requirement(course_name),
                'field_trip': random.choices([True, False], weights=[0.1, 0.9])[0],
                'online_resources': self._generate_online_resources(),
                'tags': self._generate_course_tags(course_name, category),
                'created_at': self.fake.date_time_between(start_date='-2y', end_date='now'),
                'updated_at': self.fake.date_time_between(start_date='-6m', end_date='now')
            }
            
            # 计算总学时
            course['total_hours'] = course['theory_hours'] + course['practice_hours']
            
            courses.append(course)
        
        # 设置先修课程关系
        self._set_prerequisites(courses)
        
        return courses
    
    def _get_course_category(self, dept_name: str) -> str:
        """根据院系名称确定课程类别"""
        if "计算机" in dept_name or "软件" in dept_name or "信息" in dept_name:
            return "计算机"
        elif "数学" in dept_name or "统计" in dept_name:
            return "数学"
        elif "物理" in dept_name:
            return "物理"
        elif "化学" in dept_name or "化工" in dept_name:
            return "化学"
        elif "经济" in dept_name:
            return "经济"
        elif "管理" in dept_name:
            return "管理"
        else:
            return random.choice(list(self.course_templates.keys()))
    
    def _translate_course_name(self, chinese_name: str) -> str:
        """翻译课程名称为英文"""
        return self.name_translations.get(chinese_name, f"{chinese_name} (English)")
    
    def _calculate_theory_hours(self, credits: int) -> int:
        """计算理论学时"""
        base_hours = credits * 16
        return random.randint(int(base_hours * 0.6), int(base_hours * 0.9))
    
    def _calculate_practice_hours(self, credits: int, course_name: str) -> int:
        """计算实践学时"""
        base_hours = credits * 16
        theory_ratio = 0.7 if "实验" in course_name or "实践" in course_name else 0.8
        practice_hours = int(base_hours * (1 - theory_ratio))
        return max(0, practice_hours)
    
    def _determine_semester(self, course_name: str, course_type: str) -> int:
        """确定开课学期"""
        if course_type == '通识':
            return random.randint(1, 2)  # 通识课程通常在低年级
        elif "高等数学" in course_name or "线性代数" in course_name:
            return random.randint(1, 2)  # 基础数学课程
        elif "概率论" in course_name or "离散数学" in course_name:
            return random.randint(3, 4)
        elif "数据结构" in course_name or "计算机网络" in course_name:
            return random.randint(3, 5)
        elif "机器学习" in course_name or "深度学习" in course_name:
            return random.randint(6, 8)  # 高级课程
        else:
            return random.randint(1, 8)
    
    def _determine_max_students(self, course_type: str, course_name: str) -> int:
        """确定最大学生数"""
        if "实验" in course_name or "实践" in course_name:
            return random.randint(20, 40)  # 实验课程人数较少
        elif course_type == '必修':
            return random.randint(80, 200)  # 必修课程人数较多
        elif course_type == '通识':
            return random.randint(100, 300)  # 通识课程人数最多
        else:
            return random.randint(30, 100)  # 选修课程
    
    def _generate_course_description(self, course_name: str) -> str:
        """生成课程描述"""
        return f"{course_name}是一门重要的专业课程，旨在培养学生的理论基础和实践能力。通过本课程的学习，学生将掌握{course_name}的基本概念、原理和方法，为后续专业课程的学习奠定坚实基础。"
    
    def _generate_learning_objectives(self, course_name: str) -> List[str]:
        """生成学习目标"""
        objectives = [
            f"掌握{course_name}的基本概念和理论",
            f"理解{course_name}的核心原理和方法",
            f"能够运用{course_name}知识解决实际问题",
            "培养分析问题和解决问题的能力",
            "提高创新思维和实践能力"
        ]
        return random.sample(objectives, random.randint(3, 5))
    
    def _generate_syllabus(self, course_name: str) -> List[Dict[str, Any]]:
        """生成课程大纲"""
        chapters = [
            {"chapter": 1, "title": f"{course_name}概述", "hours": 4},
            {"chapter": 2, "title": "基础理论", "hours": 8},
            {"chapter": 3, "title": "核心概念", "hours": 8},
            {"chapter": 4, "title": "实践应用", "hours": 6},
            {"chapter": 5, "title": "案例分析", "hours": 4},
            {"chapter": 6, "title": "前沿发展", "hours": 2}
        ]
        return random.sample(chapters, random.randint(4, 6))
    
    def _generate_assessment_breakdown(self) -> Dict[str, float]:
        """生成考核方式分解"""
        methods = ['期末考试', '期中考试', '平时作业', '实验报告', '课堂表现', '项目作业']
        breakdown = {}
        
        # 确保期末考试占主要比重
        breakdown['期末考试'] = random.uniform(0.4, 0.6)
        remaining = 1.0 - breakdown['期末考试']
        
        # 随机分配其他部分
        other_methods = random.sample(methods[1:], random.randint(2, 4))
        for i, method in enumerate(other_methods):
            if i == len(other_methods) - 1:
                breakdown[method] = remaining
            else:
                weight = random.uniform(0.1, remaining * 0.5)
                breakdown[method] = weight
                remaining -= weight
        
        return breakdown

    def _generate_textbook(self, course_name: str) -> Dict[str, str]:
        """生成教材信息"""
        return {
            'title': f"{course_name}教程",
            'author': self.fake.name(),
            'publisher': random.choice(['清华大学出版社', '北京大学出版社', '机械工业出版社', '电子工业出版社']),
            'edition': f"第{random.randint(1, 5)}版",
            'year': random.randint(2018, 2024),
            'isbn': self.fake.isbn13()
        }

    def _generate_reference_books(self, course_name: str) -> List[Dict[str, str]]:
        """生成参考书目"""
        num_books = random.randint(2, 5)
        books = []

        for i in range(num_books):
            book = {
                'title': f"{course_name}参考书{i+1}",
                'author': self.fake.name(),
                'publisher': random.choice(['高等教育出版社', '科学出版社', '人民邮电出版社']),
                'year': random.randint(2015, 2023)
            }
            books.append(book)

        return books

    def _generate_teaching_methods(self) -> List[str]:
        """生成教学方法"""
        methods = [
            '讲授法', '案例教学', '讨论式教学', '实验教学',
            '项目驱动', '翻转课堂', '在线教学', '混合式教学',
            '小组合作', '问题导向', '实践教学', '演示教学'
        ]
        return random.sample(methods, random.randint(2, 4))

    def _determine_difficulty_level(self, course_name: str) -> str:
        """确定课程难度等级"""
        if any(keyword in course_name for keyword in ['高等', '理论', '原理']):
            return random.choices(['中等', '困难'], weights=[0.6, 0.4])[0]
        elif any(keyword in course_name for keyword in ['导论', '概述', '基础']):
            return random.choices(['简单', '中等'], weights=[0.7, 0.3])[0]
        elif any(keyword in course_name for keyword in ['深度', '高级', '前沿']):
            return '困难'
        else:
            return random.choices(['简单', '中等', '困难'], weights=[0.3, 0.5, 0.2])[0]

    def _generate_classroom_requirements(self, course_name: str) -> List[str]:
        """生成教室要求"""
        requirements = ['普通教室']

        if "实验" in course_name or "实践" in course_name:
            requirements = ['实验室']
        elif "计算机" in course_name or "编程" in course_name:
            requirements = ['机房', '多媒体教室']
        elif "设计" in course_name or "绘图" in course_name:
            requirements = ['设计室', '多媒体教室']
        elif any(keyword in course_name for keyword in ['大', '概论', '导论']):
            requirements = ['阶梯教室', '多媒体教室']

        return requirements

    def _generate_equipment_requirements(self, course_name: str) -> List[str]:
        """生成设备要求"""
        basic_equipment = ['投影仪', '音响']

        if "计算机" in course_name or "编程" in course_name:
            return basic_equipment + ['电脑', '网络', '编程软件']
        elif "实验" in course_name:
            return basic_equipment + ['实验设备', '安全设施']
        elif "多媒体" in course_name or "设计" in course_name:
            return basic_equipment + ['设计软件', '绘图板']
        else:
            return basic_equipment

    def _generate_withdrawal_deadline(self) -> str:
        """生成退课截止时间"""
        weeks = random.randint(2, 6)
        return f"开课后第{weeks}周"

    def _has_lab_requirement(self, course_name: str) -> bool:
        """判断是否需要实验"""
        lab_keywords = ['实验', '实践', '计算机', '编程', '设计', '制作']
        return any(keyword in course_name for keyword in lab_keywords)

    def _generate_online_resources(self) -> List[Dict[str, str]]:
        """生成在线资源"""
        resources = []
        resource_types = [
            {'type': '视频课程', 'platform': '学堂在线'},
            {'type': 'MOOC课程', 'platform': '中国大学MOOC'},
            {'type': '电子书', 'platform': '超星数字图书馆'},
            {'type': '学术论文', 'platform': '知网'},
            {'type': '编程练习', 'platform': 'LeetCode'}
        ]

        num_resources = random.randint(1, 3)
        selected = random.sample(resource_types, num_resources)

        for resource in selected:
            resources.append({
                'type': resource['type'],
                'platform': resource['platform'],
                'url': f"http://{resource['platform'].lower()}.com/course"
            })

        return resources

    def _generate_course_tags(self, course_name: str, category: str) -> List[str]:
        """生成课程标签"""
        tags = [category]

        # 根据课程名称添加特定标签
        if "基础" in course_name or "导论" in course_name:
            tags.append("基础课程")
        if "高级" in course_name or "深度" in course_name:
            tags.append("高级课程")
        if "实验" in course_name or "实践" in course_name:
            tags.append("实践课程")
        if "设计" in course_name:
            tags.append("设计类")
        if "管理" in course_name:
            tags.append("管理类")
        if "工程" in course_name:
            tags.append("工程类")

        # 添加一些通用标签
        general_tags = ["理论与实践结合", "创新思维", "团队合作", "问题解决"]
        tags.extend(random.sample(general_tags, random.randint(1, 2)))

        return list(set(tags))  # 去重

    def _set_prerequisites(self, courses: List[Dict[str, Any]]) -> None:
        """设置先修课程关系"""
        # 按学期排序，确保先修关系的合理性
        courses_by_semester = {}
        for course in courses:
            semester = course['semester']
            if semester not in courses_by_semester:
                courses_by_semester[semester] = []
            courses_by_semester[semester].append(course)

        # 为每门课程设置先修课程
        for course in courses:
            prerequisites = self._find_prerequisites(course, courses_by_semester)
            course['prerequisites'] = [p['id'] for p in prerequisites]

    def _find_prerequisites(self, course: Dict[str, Any],
                          courses_by_semester: Dict[int, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """为课程查找合适的先修课程"""
        prerequisites = []
        course_name = course['name']
        course_semester = course['semester']

        # 定义先修关系规则
        prerequisite_rules = {
            '数据结构与算法': ['高等数学', '线性代数', '离散数学'],
            '计算机网络': ['数据结构与算法', '计算机组成原理'],
            '操作系统': ['数据结构与算法', '计算机组成原理'],
            '数据库系统': ['数据结构与算法'],
            '软件工程': ['数据结构与算法', '计算机网络'],
            '机器学习': ['高等数学', '线性代数', '概率论与数理统计'],
            '深度学习': ['机器学习', '高等数学', '线性代数'],
            '概率论与数理统计': ['高等数学'],
            '线性代数': ['高等数学'],
            '微观经济学': ['高等数学'],
            '宏观经济学': ['微观经济学'],
            '理论力学': ['高等数学', '大学物理'],
            '电磁学': ['大学物理', '高等数学']
        }

        # 查找规则中定义的先修课程
        if course_name in prerequisite_rules:
            required_prereqs = prerequisite_rules[course_name]

            # 在较早学期中查找这些先修课程
            for semester in range(1, course_semester):
                if semester in courses_by_semester:
                    for candidate in courses_by_semester[semester]:
                        if candidate['name'] in required_prereqs:
                            prerequisites.append(candidate)

        # 如果没有找到规则定义的先修课程，随机选择一些较早学期的课程
        if not prerequisites and course_semester > 2:
            # 从前面的学期中随机选择0-2门课程作为先修课程
            num_prereqs = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]

            if num_prereqs > 0:
                available_courses = []
                for semester in range(max(1, course_semester - 3), course_semester):
                    if semester in courses_by_semester:
                        available_courses.extend(courses_by_semester[semester])

                if available_courses:
                    selected = random.sample(available_courses,
                                           min(num_prereqs, len(available_courses)))
                    prerequisites.extend(selected)

        return prerequisites
