# file: data-generator/generators/department.py
# 功能: 院系专业数据生成器

import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from faker import Faker

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEPARTMENT_CONFIG


class DepartmentGenerator:
    """院系数据生成器
    
    负责生成真实的院系和专业数据，包括：
    - 院系基本信息
    - 专业信息和院系关联
    - 院系领导信息
    - 建立时间等历史数据
    """
    
    def __init__(self, locale: str = 'zh_CN'):
        """初始化生成器
        
        Args:
            locale: 本地化设置，默认为中文
        """
        self.fake = Faker(locale)
        self.department_templates = DEPARTMENT_CONFIG['templates']
        self.major_mapping = DEPARTMENT_CONFIG['major_mapping']
        
        # 设置随机种子以确保可重现性
        Faker.seed(42)
        random.seed(42)
    
    def generate_departments(self, count: int) -> List[Dict[str, Any]]:
        """生成院系数据
        
        Args:
            count: 要生成的院系数量
            
        Returns:
            院系数据列表
        """
        departments = []
        
        # 确保不超过模板数量
        actual_count = min(count, len(self.department_templates))
        selected_names = random.sample(self.department_templates, actual_count)
        
        for i, name in enumerate(selected_names):
            department = {
                'id': i + 1,
                'name': name,
                'code': f"DEPT{i+1:03d}",
                'dean': self.fake.name(),
                'dean_title': random.choice(['教授', '副教授']),
                'phone': self.fake.phone_number(),
                'email': f"dean{i+1}@university.edu.cn",
                'office_address': f"{name}大楼{random.randint(101, 999)}室",
                'building_location': f"{name}大楼",
                'established_year': random.randint(1950, 2020),
                'staff_count': random.randint(20, 150),
                'student_count': random.randint(500, 3000),
                'description': f"{name}致力于培养高素质的专业人才，在教学和科研方面具有显著优势。",
                'website': f"http://{self._generate_domain_name(name)}.university.edu.cn",
                'budget': random.randint(1000000, 10000000),  # 年度预算（元）
                'research_areas': self._generate_research_areas(name),
                'achievements': self._generate_achievements(),
                'is_active': True,
                'created_at': self.fake.date_time_between(start_date='-5y', end_date='now'),
                'updated_at': self.fake.date_time_between(start_date='-1y', end_date='now')
            }
            departments.append(department)
        
        return departments
    
    def generate_majors(self, departments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成专业数据
        
        Args:
            departments: 院系数据列表
            
        Returns:
            专业数据列表
        """
        majors = []
        major_id = 1
        
        for dept in departments:
            dept_name = dept['name']
            
            # 获取该院系的专业模板
            if dept_name in self.major_mapping:
                major_names = self.major_mapping[dept_name]
            else:
                # 为其他院系生成通用专业名称
                base_name = dept_name.replace('学院', '').replace('系', '')
                major_names = [
                    f"{base_name}专业",
                    f"应用{base_name}",
                    f"{base_name}技术"
                ]
            
            for major_name in major_names:
                degree_type = random.choice(['本科', '硕士', '博士'])
                
                major = {
                    'id': major_id,
                    'name': major_name,
                    'code': f"MAJ{major_id:03d}",
                    'english_name': self._translate_major_name(major_name),
                    'department_id': dept['id'],
                    'degree_type': degree_type,
                    'duration': self._get_duration_by_degree(degree_type),
                    'total_credits': self._get_credits_by_degree(degree_type),
                    'tuition_fee': random.randint(5000, 15000),  # 年学费
                    'enrollment_quota': random.randint(30, 200),  # 招生名额
                    'current_students': random.randint(100, 800),  # 在校生数
                    'employment_rate': round(random.uniform(0.85, 0.98), 3),  # 就业率
                    'description': f"{major_name}专业培养具有扎实理论基础和实践能力的高级专门人才。",
                    'objectives': self._generate_training_objectives(major_name),
                    'core_courses': self._generate_core_courses(major_name),
                    'career_prospects': self._generate_career_prospects(major_name),
                    'admission_requirements': self._generate_admission_requirements(degree_type),
                    'is_active': random.choices([True, False], weights=[0.95, 0.05])[0],
                    'accreditation': random.choices(['已认证', '待认证', '未认证'], weights=[0.8, 0.15, 0.05])[0],
                    'ranking': random.randint(1, 100) if random.random() < 0.3 else None,
                    'created_at': self.fake.date_time_between(start_date='-3y', end_date='now'),
                    'updated_at': self.fake.date_time_between(start_date='-6m', end_date='now')
                }
                majors.append(major)
                major_id += 1
        
        return majors
    
    def _generate_domain_name(self, dept_name: str) -> str:
        """生成院系域名"""
        # 简化院系名称作为域名
        domain_map = {
            '计算机科学与技术学院': 'cs',
            '软件学院': 'software',
            '信息工程学院': 'ie',
            '电子信息工程学院': 'eie',
            '机械工程学院': 'me',
            '经济管理学院': 'em',
            '医学院': 'med',
            '外国语学院': 'fl'
        }
        return domain_map.get(dept_name, 'dept')
    
    def _generate_research_areas(self, dept_name: str) -> List[str]:
        """生成研究领域"""
        research_map = {
            '计算机科学与技术学院': ['人工智能', '机器学习', '计算机视觉', '自然语言处理', '分布式系统'],
            '电子信息工程学院': ['信号处理', '通信技术', '集成电路设计', '物联网技术'],
            '机械工程学院': ['智能制造', '机器人技术', '新材料应用', '绿色制造'],
            '经济管理学院': ['数字经济', '供应链管理', '金融科技', '企业战略'],
            '医学院': ['精准医学', '生物医学工程', '临床研究', '公共卫生']
        }
        
        default_areas = ['基础理论研究', '应用技术开发', '产学研合作']
        areas = research_map.get(dept_name, default_areas)
        return random.sample(areas, random.randint(2, min(4, len(areas))))
    
    def _generate_achievements(self) -> List[str]:
        """生成学院成就"""
        achievements = [
            '国家级教学成果奖',
            '省级科技进步奖',
            '优秀教学团队',
            '重点实验室建设',
            '国际合作项目',
            '产学研合作基地',
            '创新创业教育示范',
            '学科建设优秀奖'
        ]
        return random.sample(achievements, random.randint(2, 5))
    
    def _translate_major_name(self, chinese_name: str) -> str:
        """翻译专业名称为英文"""
        translations = {
            '计算机科学与技术': 'Computer Science and Technology',
            '软件工程': 'Software Engineering',
            '网络工程': 'Network Engineering',
            '信息安全': 'Information Security',
            '数据科学与大数据技术': 'Data Science and Big Data Technology',
            '人工智能': 'Artificial Intelligence',
            '电子信息工程': 'Electronic Information Engineering',
            '通信工程': 'Communication Engineering',
            '机械设计制造及其自动化': 'Mechanical Design Manufacturing and Automation',
            '工商管理': 'Business Administration',
            '临床医学': 'Clinical Medicine'
        }
        return translations.get(chinese_name, f"{chinese_name} (English)")
    
    def _get_duration_by_degree(self, degree_type: str) -> int:
        """根据学位类型获取学制"""
        duration_map = {
            '本科': 4,
            '硕士': random.choice([2, 3]),
            '博士': random.choice([3, 4])
        }
        return duration_map.get(degree_type, 4)
    
    def _get_credits_by_degree(self, degree_type: str) -> int:
        """根据学位类型获取总学分"""
        credits_map = {
            '本科': random.randint(140, 180),
            '硕士': random.randint(30, 50),
            '博士': random.randint(18, 30)
        }
        return credits_map.get(degree_type, 160)
    
    def _generate_training_objectives(self, major_name: str) -> str:
        """生成培养目标"""
        return f"培养具有{major_name}专业知识和技能，能够在相关领域从事研究、开发、管理等工作的高级专门人才。"
    
    def _generate_core_courses(self, major_name: str) -> List[str]:
        """生成核心课程"""
        course_map = {
            '计算机科学与技术': ['数据结构', '算法设计', '计算机网络', '操作系统', '数据库系统'],
            '软件工程': ['软件需求工程', '软件设计', '软件测试', '项目管理', '软件架构'],
            '电子信息工程': ['电路分析', '信号与系统', '数字信号处理', '通信原理', '电磁场理论'],
            '机械设计制造及其自动化': ['机械设计', '制造工艺', '自动控制', '机械制图', '材料力学'],
            '工商管理': ['管理学原理', '市场营销', '财务管理', '人力资源管理', '战略管理']
        }
        
        default_courses = ['专业基础课', '专业核心课', '实践课程', '毕业设计']
        courses = course_map.get(major_name, default_courses)
        return random.sample(courses, random.randint(3, len(courses)))
    
    def _generate_career_prospects(self, major_name: str) -> List[str]:
        """生成就业前景"""
        prospects_map = {
            '计算机科学与技术': ['软件开发工程师', 'IT项目经理', '系统架构师', '技术总监'],
            '软件工程': ['软件工程师', '产品经理', '技术顾问', '创业者'],
            '电子信息工程': ['硬件工程师', '系统集成工程师', '技术支持', '研发工程师'],
            '工商管理': ['企业管理者', '咨询顾问', '市场分析师', '创业者'],
            '临床医学': ['临床医师', '医学研究员', '医院管理者', '医疗顾问']
        }
        
        default_prospects = ['专业技术人员', '管理人员', '研究人员', '自主创业']
        prospects = prospects_map.get(major_name, default_prospects)
        return random.sample(prospects, random.randint(2, len(prospects)))
    
    def _generate_admission_requirements(self, degree_type: str) -> Dict[str, Any]:
        """生成入学要求"""
        if degree_type == '本科':
            return {
                'entrance_exam': '高考',
                'min_score': random.randint(500, 650),
                'subjects': ['数学', '英语', '物理/化学'],
                'additional_requirements': '无色盲色弱'
            }
        elif degree_type == '硕士':
            return {
                'entrance_exam': '研究生入学考试',
                'min_score': random.randint(300, 400),
                'subjects': ['政治', '英语', '数学', '专业课'],
                'additional_requirements': '本科学位'
            }
        else:  # 博士
            return {
                'entrance_exam': '博士入学考试',
                'min_score': random.randint(200, 300),
                'subjects': ['英语', '专业课'],
                'additional_requirements': '硕士学位，发表学术论文'
            }
