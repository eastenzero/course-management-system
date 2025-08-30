# file: data-generator/generators/user.py
# 功能: 用户数据生成器

import random
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from faker import Faker

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import USER_CONFIG


class UserGenerator:
    """用户数据生成器
    
    负责生成学生和教师数据，包括：
    - 真实的中文姓名
    - 个人基本信息
    - 学术信息和职业信息
    - 联系方式和地址
    """
    
    def __init__(self, locale: str = 'zh_CN'):
        """初始化生成器
        
        Args:
            locale: 本地化设置，默认为中文
        """
        self.fake = Faker(locale)
        self.surnames = USER_CONFIG['surnames']
        self.given_names = USER_CONFIG['given_names']
        self.teacher_titles = USER_CONFIG['teacher_titles']
        self.teacher_title_weights = USER_CONFIG['teacher_title_weights']
        self.degrees = USER_CONFIG['degrees']
        self.degree_weights = USER_CONFIG['degree_weights']
        
        # 设置随机种子
        Faker.seed(42)
        random.seed(42)
    
    def generate_students(self, count: int, majors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成学生数据
        
        Args:
            count: 要生成的学生数量
            majors: 专业数据列表
            
        Returns:
            学生数据列表
        """
        students = []
        
        for i in range(count):
            major = random.choice(majors)
            grade = random.randint(2020, 2024)  # 入学年份
            birth_year = grade - random.randint(18, 22)  # 入学时年龄18-22岁
            
            student = {
                'id': i + 1,
                'student_id': self._generate_student_id(grade, major['department_id'], i + 1),
                'username': f"student{i+1:06d}",
                'password_hash': self._generate_password_hash(),
                'name': self.generate_chinese_name(),
                'gender': random.choice(['男', '女']),
                'birth_date': self._generate_birth_date(birth_year),
                'id_card': self._generate_id_card(),
                'phone': self.fake.phone_number(),
                'email': f"student{i+1}@university.edu.cn",
                'personal_email': self.fake.email(),
                'major_id': major['id'],
                'grade': grade,
                'class_number': random.randint(1, 10),
                'student_type': random.choices(['普通', '交换生', '留学生'], weights=[0.9, 0.05, 0.05])[0],
                'enrollment_status': random.choices(['在读', '休学', '退学', '毕业'], weights=[0.85, 0.1, 0.02, 0.03])[0],
                'academic_status': random.choices(['正常', '试读', '留级'], weights=[0.9, 0.05, 0.05])[0],
                'gpa': round(random.uniform(2.0, 4.0), 2),
                'total_credits': random.randint(0, 150),
                'completed_credits': random.randint(0, 120),
                'scholarship_level': self._generate_scholarship(),
                'home_address': self.fake.address(),
                'dormitory': self._generate_dormitory_info(),
                'emergency_contact': self.generate_chinese_name(),
                'emergency_phone': self.fake.phone_number(),
                'emergency_relationship': random.choice(['父亲', '母亲', '监护人', '其他亲属']),
                'political_status': random.choices(['群众', '团员', '党员'], weights=[0.3, 0.6, 0.1])[0],
                'ethnicity': random.choices(['汉族', '回族', '蒙古族', '藏族', '其他'], weights=[0.9, 0.03, 0.02, 0.02, 0.03])[0],
                'health_status': random.choices(['健康', '一般', '有慢性病'], weights=[0.85, 0.12, 0.03])[0],
                'hobbies': self._generate_hobbies(),
                'skills': self._generate_student_skills(),
                'awards': self._generate_student_awards(),
                'social_activities': self._generate_social_activities(),
                'internship_experience': self._generate_internship_experience(),
                'is_active': True,
                'last_login': self.fake.date_time_between(start_date='-30d', end_date='now'),
                'created_at': self.fake.date_time_between(start_date='-4y', end_date='now'),
                'updated_at': self.fake.date_time_between(start_date='-1m', end_date='now')
            }
            students.append(student)
        
        return students
    
    def generate_teachers(self, count: int, departments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成教师数据
        
        Args:
            count: 要生成的教师数量
            departments: 院系数据列表
            
        Returns:
            教师数据列表
        """
        teachers = []
        
        for i in range(count):
            department = random.choice(departments)
            birth_year = random.randint(1960, 1995)  # 教师年龄范围
            
            teacher = {
                'id': i + 1,
                'employee_id': f"T{i+1:06d}",
                'username': f"teacher{i+1:06d}",
                'password_hash': self._generate_password_hash(),
                'name': self.generate_chinese_name(),
                'gender': random.choice(['男', '女']),
                'birth_date': self._generate_birth_date(birth_year),
                'id_card': self._generate_id_card(),
                'phone': self.fake.phone_number(),
                'email': f"teacher{i+1}@university.edu.cn",
                'personal_email': self.fake.email(),
                'department_id': department['id'],
                'title': random.choices(self.teacher_titles, weights=self.teacher_title_weights)[0],
                'degree': random.choices(self.degrees, weights=self.degree_weights)[0],
                'graduation_school': self._generate_graduation_school(),
                'major_field': self._generate_major_field(department['name']),
                'hire_date': self.fake.date_between(start_date='-20y', end_date='now'),
                'employment_type': random.choices(['全职', '兼职', '客座'], weights=[0.85, 0.1, 0.05])[0],
                'employment_status': random.choices(['在职', '退休', '离职'], weights=[0.9, 0.08, 0.02])[0],
                'office_location': f"{department['name']}{random.randint(101, 999)}室",
                'office_phone': self.fake.phone_number(),
                'research_areas': self.generate_research_areas(department['name']),
                'teaching_areas': self._generate_teaching_areas(),
                'max_weekly_hours': random.randint(12, 20),
                'preferred_time_slots': self._generate_preferred_time_slots(),
                'salary_level': random.randint(8000, 25000),
                'home_address': self.fake.address(),
                'marital_status': random.choices(['未婚', '已婚', '离异', '丧偶'], weights=[0.2, 0.7, 0.08, 0.02])[0],
                'political_status': random.choices(['群众', '党员', '民主党派'], weights=[0.4, 0.55, 0.05])[0],
                'publications': self._generate_publications(),
                'projects': self._generate_research_projects(),
                'awards': self._generate_teacher_awards(),
                'academic_positions': self._generate_academic_positions(),
                'international_experience': self._generate_international_experience(),
                'languages': self._generate_language_skills(),
                'is_active': True,
                'last_login': self.fake.date_time_between(start_date='-7d', end_date='now'),
                'created_at': self.fake.date_time_between(start_date='-5y', end_date='now'),
                'updated_at': self.fake.date_time_between(start_date='-1w', end_date='now')
            }
            teachers.append(teacher)
        
        return teachers
    
    def generate_chinese_name(self) -> str:
        """生成中文姓名"""
        surname = random.choice(self.surnames)
        given_name_length = random.choices([1, 2], weights=[0.3, 0.7])[0]
        given_name = ''.join(random.choices(self.given_names, k=given_name_length))
        return surname + given_name
    
    def _generate_student_id(self, grade: int, dept_id: int, sequence: int) -> str:
        """生成学号"""
        return f"{grade}{dept_id:02d}{sequence:04d}"
    
    def _generate_password_hash(self) -> str:
        """生成密码哈希（模拟）"""
        return f"$2b$12${self.fake.sha256()[:22]}"
    
    def _generate_birth_date(self, birth_year: int) -> date:
        """生成出生日期"""
        return self.fake.date_between(
            start_date=date(birth_year, 1, 1),
            end_date=date(birth_year, 12, 31)
        )
    
    def _generate_id_card(self) -> str:
        """生成身份证号（模拟）"""
        return self.fake.ssn()
    
    def _generate_scholarship(self) -> Optional[str]:
        """生成奖学金等级"""
        scholarships = ['国家奖学金', '国家励志奖学金', '校级奖学金', '院级奖学金']
        return random.choice([None] + scholarships) if random.random() < 0.3 else None
    
    def _generate_dormitory_info(self) -> Dict[str, Any]:
        """生成宿舍信息"""
        building_num = random.randint(1, 20)
        room_num = random.randint(101, 699)
        return {
            'building': f"{building_num}号楼",
            'room': f"{room_num}",
            'bed': random.randint(1, 4),
            'full_address': f"{building_num}号楼{room_num}室"
        }
    
    def _generate_hobbies(self) -> List[str]:
        """生成兴趣爱好"""
        hobbies = [
            '阅读', '运动', '音乐', '绘画', '摄影', '旅行', '编程',
            '游戏', '电影', '书法', '舞蹈', '唱歌', '篮球', '足球',
            '羽毛球', '乒乓球', '游泳', '跑步', '健身', '瑜伽'
        ]
        return random.sample(hobbies, random.randint(2, 5))
    
    def _generate_student_skills(self) -> List[str]:
        """生成学生技能"""
        skills = [
            'Python编程', 'Java编程', 'C++编程', 'JavaScript',
            'HTML/CSS', 'SQL数据库', 'Office办公软件', 'Photoshop',
            '英语四级', '英语六级', '托福', '雅思', '驾驶证',
            '计算机二级', '普通话二甲', '会计从业资格'
        ]
        return random.sample(skills, random.randint(2, 6))
    
    def _generate_student_awards(self) -> List[str]:
        """生成学生获奖情况"""
        awards = [
            '三好学生', '优秀学生干部', '优秀团员', '学习优秀奖',
            '社会实践先进个人', '志愿服务优秀奖', '创新创业大赛奖',
            '数学建模竞赛奖', 'ACM程序设计竞赛奖', '英语演讲比赛奖'
        ]
        num_awards = random.choices([0, 1, 2, 3], weights=[0.4, 0.3, 0.2, 0.1])[0]
        return random.sample(awards, num_awards) if num_awards > 0 else []
    
    def _generate_social_activities(self) -> List[str]:
        """生成社会活动"""
        activities = [
            '学生会干部', '社团负责人', '班级委员', '志愿者服务',
            '社会实践活动', '文艺演出', '体育比赛', '学术讲座',
            '创业项目', '实习实训', '国际交流', '科研项目'
        ]
        num_activities = random.choices([0, 1, 2, 3], weights=[0.3, 0.4, 0.2, 0.1])[0]
        return random.sample(activities, num_activities) if num_activities > 0 else []
    
    def _generate_internship_experience(self) -> List[Dict[str, Any]]:
        """生成实习经历"""
        if random.random() < 0.4:  # 40%的学生有实习经历
            companies = ['腾讯', '阿里巴巴', '百度', '字节跳动', '华为', '小米', '美团', '滴滴']
            positions = ['软件开发实习生', '产品经理实习生', '数据分析实习生', '运营实习生']
            
            return [{
                'company': random.choice(companies),
                'position': random.choice(positions),
                'duration': f"{random.randint(1, 6)}个月",
                'description': '参与项目开发，学习实践技能'
            }]
        return []

    def _generate_graduation_school(self) -> str:
        """生成毕业院校"""
        schools = [
            '清华大学', '北京大学', '中国科学院大学', '复旦大学', '上海交通大学',
            '浙江大学', '南京大学', '中山大学', '华中科技大学', '西安交通大学',
            '哈尔滨工业大学', '北京理工大学', '东南大学', '天津大学', '华南理工大学'
        ]
        return random.choice(schools)

    def _generate_major_field(self, dept_name: str) -> str:
        """根据院系生成专业领域"""
        field_map = {
            '计算机科学与技术学院': ['计算机科学', '软件工程', '人工智能', '网络安全'],
            '电子信息工程学院': ['电子工程', '通信工程', '信号处理', '集成电路'],
            '机械工程学院': ['机械工程', '自动化', '材料工程', '工业设计'],
            '经济管理学院': ['管理学', '经济学', '金融学', '会计学'],
            '医学院': ['临床医学', '基础医学', '公共卫生', '药学']
        }

        fields = field_map.get(dept_name, ['相关专业'])
        return random.choice(fields)

    def generate_research_areas(self, dept_name: str) -> List[str]:
        """生成研究方向"""
        research_map = {
            '计算机科学与技术学院': [
                '机器学习', '深度学习', '计算机视觉', '自然语言处理',
                '数据挖掘', '软件工程', '网络安全', '分布式系统',
                '人工智能', '算法设计', '数据库系统', '云计算'
            ],
            '电子信息工程学院': [
                '信号处理', '通信技术', '图像处理', '嵌入式系统',
                '物联网', '5G技术', '集成电路设计', '射频技术'
            ],
            '机械工程学院': [
                '智能制造', '机器人技术', '新材料', '绿色制造',
                '精密加工', '自动化控制', '工业4.0', '3D打印'
            ],
            '经济管理学院': [
                '数字经济', '供应链管理', '金融科技', '企业战略',
                '市场营销', '人力资源', '组织行为', '创新管理'
            ]
        }

        default_areas = ['基础理论研究', '应用技术开发', '产学研合作']
        areas = research_map.get(dept_name, default_areas)
        return random.sample(areas, random.randint(1, 3))

    def _generate_teaching_areas(self) -> List[str]:
        """生成教学领域"""
        areas = [
            '本科生教学', '研究生教学', '博士生指导', '实验教学',
            '课程设计', '毕业设计指导', '实习指导', '在线教学'
        ]
        return random.sample(areas, random.randint(2, 4))

    def _generate_preferred_time_slots(self) -> List[str]:
        """生成偏好时间段"""
        slots = ['上午', '下午', '晚上']
        weights = [0.6, 0.8, 0.3]  # 上午和下午更受欢迎

        preferred = []
        for slot, weight in zip(slots, weights):
            if random.random() < weight:
                preferred.append(slot)

        return preferred if preferred else ['上午']

    def _generate_publications(self) -> List[Dict[str, Any]]:
        """生成发表论文"""
        num_papers = random.choices([0, 1, 2, 3, 4, 5], weights=[0.2, 0.3, 0.25, 0.15, 0.08, 0.02])[0]

        publications = []
        for i in range(num_papers):
            pub = {
                'title': f"Research on {self.fake.catch_phrase()}",
                'journal': random.choice(['IEEE Transactions', 'ACM Computing', 'Nature', 'Science', '中文核心期刊']),
                'year': random.randint(2018, 2024),
                'impact_factor': round(random.uniform(1.0, 10.0), 2),
                'citation_count': random.randint(0, 100)
            }
            publications.append(pub)

        return publications

    def _generate_research_projects(self) -> List[Dict[str, Any]]:
        """生成科研项目"""
        num_projects = random.choices([0, 1, 2, 3], weights=[0.3, 0.4, 0.2, 0.1])[0]

        projects = []
        project_types = ['国家自然科学基金', '省部级项目', '横向合作项目', '校级项目']

        for i in range(num_projects):
            project = {
                'name': f"{self.fake.catch_phrase()}研究",
                'type': random.choice(project_types),
                'funding': random.randint(10000, 1000000),
                'duration': f"{random.randint(1, 5)}年",
                'role': random.choice(['主持', '参与', '合作'])
            }
            projects.append(project)

        return projects

    def _generate_teacher_awards(self) -> List[str]:
        """生成教师获奖情况"""
        awards = [
            '优秀教师', '教学名师', '师德标兵', '科研先进个人',
            '优秀共产党员', '三育人先进个人', '教学成果奖', '科技进步奖',
            '优秀指导教师', '学科带头人', '青年教师奖', '国务院特殊津贴'
        ]

        num_awards = random.choices([0, 1, 2, 3], weights=[0.4, 0.35, 0.2, 0.05])[0]
        return random.sample(awards, num_awards) if num_awards > 0 else []

    def _generate_academic_positions(self) -> List[str]:
        """生成学术职务"""
        positions = [
            '学术委员会委员', '学位委员会委员', '教学委员会委员',
            '期刊编委', '学会理事', '专业委员会委员',
            '博士生导师', '硕士生导师', '学科带头人'
        ]

        num_positions = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
        return random.sample(positions, num_positions) if num_positions > 0 else []

    def _generate_international_experience(self) -> List[Dict[str, Any]]:
        """生成国际经历"""
        if random.random() < 0.3:  # 30%的教师有国际经历
            countries = ['美国', '英国', '德国', '日本', '澳大利亚', '加拿大', '新加坡']
            purposes = ['访问学者', '博士后研究', '学术会议', '合作研究', '进修学习']

            return [{
                'country': random.choice(countries),
                'institution': f"{random.choice(countries)} University",
                'purpose': random.choice(purposes),
                'duration': f"{random.randint(3, 24)}个月",
                'year': random.randint(2015, 2023)
            }]
        return []

    def _generate_language_skills(self) -> List[Dict[str, str]]:
        """生成语言技能"""
        languages = [
            {'language': '英语', 'level': random.choice(['良好', '熟练', '精通'])},
            {'language': '中文', 'level': '母语'}
        ]

        # 可能的第三语言
        if random.random() < 0.2:
            third_langs = ['日语', '德语', '法语', '俄语', '韩语']
            languages.append({
                'language': random.choice(third_langs),
                'level': random.choice(['入门', '良好'])
            })

        return languages
