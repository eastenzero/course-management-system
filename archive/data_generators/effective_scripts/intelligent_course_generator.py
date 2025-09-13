#!/usr/bin/env python
"""
智能课程数据生成器 - 生成符合排课算法约束的课程数据
针对80万学生规模，生成15,000门合理的课程数据
"""

# 设置环境变量，禁用有问题的模块
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'course_management.settings'
os.environ['DISABLE_MAGIC'] = '1'  # 禁用magic模块

import sys
import django
import random
import json
from datetime import datetime, time, date
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from faker import Faker
import math

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# 修改magic模块导入问题
import builtins
original_import = builtins.__import__

def patched_import(name, *args, **kwargs):
    if name == 'magic':
        # 创建一个虚拟magic模块
        class FakeMagic:
            def from_buffer(self, buffer, mime=False):
                return 'application/octet-stream'
        
        class MockMagic:
            Magic = FakeMagic
            
        return MockMagic()
    return original_import(name, *args, **kwargs)

builtins.__import__ = patched_import

try:
    django.setup()
except Exception as e:
    print(f"警告: Django初始化问题: {e}")
    print("尝试继续运行...")

from django.contrib.auth import get_user_model
from apps.courses.models import Course
from apps.classrooms.models import Building, Classroom
from django.db import transaction
from django.utils import timezone

User = get_user_model()
fake = Faker('zh_CN')

@dataclass
class CourseGenerationConfig:
    """课程生成配置"""
    target_courses: int = 15000
    batch_size: int = 1000
    
    # 学期配置
    academic_year: str = "2024-2025"
    semester_fall: str = "2024-2025-1"
    semester_spring: str = "2024-2025-2"

class IntelligentCourseGenerator:
    """智能课程生成器"""
    
    def __init__(self, config: CourseGenerationConfig):
        self.config = config
        self.fake = Faker('zh_CN')
        
        # 院系与专业配置（与现有教师数据匹配）
        self.departments = {
            "计算机学院": {
                "majors": ["计算机科学与技术", "软件工程", "网络工程", "数据科学与大数据技术", "人工智能"],
                "course_categories": ["编程基础", "算法设计", "数据结构", "操作系统", "数据库", "网络技术", "人工智能", "软件工程"]
            },
            "数学学院": {
                "majors": ["数学与应用数学", "信息与计算科学", "统计学", "金融数学"],
                "course_categories": ["高等数学", "线性代数", "概率统计", "数值分析", "数学建模", "金融数学"]
            },
            "物理学院": {
                "majors": ["物理学", "应用物理学", "光电信息科学与工程", "材料物理"],
                "course_categories": ["普通物理", "理论物理", "实验物理", "光学", "电子技术", "材料科学"]
            },
            "化学学院": {
                "majors": ["化学", "应用化学", "材料化学", "化学工程与工艺"],
                "course_categories": ["无机化学", "有机化学", "物理化学", "分析化学", "化工原理", "材料化学"]
            },
            "生物学院": {
                "majors": ["生物科学", "生物技术", "生物信息学", "生态学"],
                "course_categories": ["细胞生物学", "分子生物学", "遗传学", "生态学", "生物技术", "生物信息学"]
            },
            "外国语学院": {
                "majors": ["英语", "日语", "法语", "德语", "俄语"],
                "course_categories": ["基础语言", "语言文学", "翻译", "语言学", "文化研究"]
            },
            "经济管理学院": {
                "majors": ["经济学", "金融学", "国际经济与贸易", "工商管理", "市场营销", "会计学"],
                "course_categories": ["经济学原理", "管理学", "财务管理", "市场营销", "国际贸易", "统计学"]
            },
            "文学院": {
                "majors": ["汉语言文学", "新闻学", "广告学", "历史学"],
                "course_categories": ["文学理论", "语言学", "新闻传播", "广告学", "历史学", "文化研究"]
            },
            "艺术学院": {
                "majors": ["音乐学", "美术学", "舞蹈学", "设计学"],
                "course_categories": ["音乐理论", "美术技法", "舞蹈技巧", "设计原理", "艺术史"]
            },
            "体育学院": {
                "majors": ["体育教育", "运动训练", "社会体育"],
                "course_categories": ["运动生理学", "体育心理学", "运动训练学", "体育教学法"]
            },
            "医学院": {
                "majors": ["临床医学", "预防医学", "护理学", "药学"],
                "course_categories": ["基础医学", "临床医学", "预防医学", "药理学", "护理学"]
            },
            "法学院": {
                "majors": ["法学", "政治学", "社会学"],
                "course_categories": ["法理学", "民法", "刑法", "行政法", "政治学", "社会学"]
            },
            "教育学院": {
                "majors": ["教育学", "心理学", "学前教育"],
                "course_categories": ["教育学原理", "心理学", "教育心理学", "学前教育", "教育技术"]
            },
            "工学院": {
                "majors": ["机械工程", "电气工程", "土木工程", "建筑学", "环境工程"],
                "course_categories": ["工程力学", "机械设计", "电路分析", "建筑设计", "环境工程"]
            },
            "材料学院": {
                "majors": ["材料科学与工程", "冶金工程", "高分子材料"],
                "course_categories": ["材料科学基础", "材料工程", "冶金工程", "高分子材料"]
            }
        }
        
        # 课程类型配置（符合排课算法）
        self.course_types = {
            'required': {
                'weight': 0.4,
                'credits_range': (3, 6),
                'hours_multiplier': 16,  # 每学分16学时
                'max_students_range': (80, 150)
            },
            'elective': {
                'weight': 0.35,
                'credits_range': (2, 4),
                'hours_multiplier': 16,
                'max_students_range': (40, 100)
            },
            'public': {
                'weight': 0.15,
                'credits_range': (1, 3),
                'hours_multiplier': 16,
                'max_students_range': (100, 200)
            },
            'professional': {
                'weight': 0.1,
                'credits_range': (2, 5),
                'hours_multiplier': 16,
                'max_students_range': (30, 80)
            }
        }
        
        # 课程模板（按学科分类）
        self.course_templates = {
            "编程基础": [
                "程序设计基础", "C语言程序设计", "C++程序设计", "Java程序设计", 
                "Python程序设计", "Web前端开发", "移动应用开发"
            ],
            "算法设计": [
                "数据结构与算法", "算法分析与设计", "计算机算法", "算法导论",
                "高级数据结构", "算法优化技术", "并行算法"
            ],
            "数据库": [
                "数据库系统原理", "数据库设计", "高级数据库系统", "分布式数据库",
                "数据仓库与挖掘", "NoSQL数据库", "大数据技术"
            ],
            "网络技术": [
                "计算机网络", "网络编程", "网络安全", "无线网络技术",
                "网络协议分析", "云计算技术", "物联网技术"
            ],
            "人工智能": [
                "人工智能导论", "机器学习", "深度学习", "神经网络",
                "自然语言处理", "计算机视觉", "知识图谱"
            ],
            "高等数学": [
                "高等数学A", "高等数学B", "数学分析", "微积分",
                "高等代数", "解析几何", "复变函数"
            ],
            "线性代数": [
                "线性代数", "矩阵论", "高等代数", "空间解析几何",
                "抽象代数", "数值线性代数"
            ],
            "概率统计": [
                "概率论与数理统计", "应用统计学", "数理统计", "随机过程",
                "多元统计分析", "时间序列分析", "统计软件应用"
            ],
            "普通物理": [
                "大学物理", "力学", "电磁学", "热学", "光学",
                "原子物理学", "量子力学", "固体物理"
            ],
            "无机化学": [
                "无机化学", "无机化学实验", "结构化学", "配位化学",
                "固体化学", "生物无机化学"
            ],
            "基础语言": [
                "综合英语", "英语听力", "英语口语", "英语写作",
                "英语阅读", "英语语法", "英语翻译"
            ],
            "经济学原理": [
                "微观经济学", "宏观经济学", "计量经济学", "国际经济学",
                "发展经济学", "货币银行学", "财政学"
            ],
            "管理学": [
                "管理学原理", "组织行为学", "人力资源管理", "战略管理",
                "运营管理", "项目管理", "质量管理"
            ],
            "文学理论": [
                "文学概论", "中国古代文学", "中国现代文学", "外国文学",
                "比较文学", "文学批评", "诗歌鉴赏"
            ]
        }
        
        # 公共课程（所有专业都需要的）
        self.public_courses = [
            ("思想道德修养与法律基础", "思政课", 3),
            ("中国近现代史纲要", "思政课", 3),
            ("马克思主义基本原理", "思政课", 3),
            ("毛泽东思想和中国特色社会主义理论体系概论", "思政课", 4),
            ("形势与政策", "思政课", 2),
            ("大学英语(一)", "外语课", 4),
            ("大学英语(二)", "外语课", 4),
            ("大学英语(三)", "外语课", 3),
            ("大学英语(四)", "外语课", 3),
            ("体育(一)", "体育课", 1),
            ("体育(二)", "体育课", 1),
            ("体育(三)", "体育课", 1),
            ("体育(四)", "体育课", 1),
            ("军事理论", "军事课", 2),
            ("大学生心理健康教育", "素质课", 2),
            ("大学生职业规划与就业指导", "素质课", 2),
            ("创新创业基础", "素质课", 2),
            ("计算机应用基础", "计算机课", 3),
            ("高等数学", "数学课", 5),
            ("线性代数", "数学课", 3),
            ("概率论与数理统计", "数学课", 3)
        ]

    def generate_courses(self) -> List[Dict]:
        """生成课程数据"""
        print(f"📚 开始生成课程数据 ({self.config.target_courses} 门)...")
        
        courses = []
        course_codes = set()
        
        # 1. 生成公共课程
        public_courses = self._generate_public_courses()
        courses.extend(public_courses)
        for course in public_courses:
            course_codes.add(course['code'])
        
        print(f"✅ 生成公共课程 {len(public_courses)} 门")
        
        # 2. 生成专业课程
        remaining_courses = self.config.target_courses - len(public_courses)
        professional_courses = self._generate_professional_courses(remaining_courses, course_codes)
        courses.extend(professional_courses)
        
        print(f"✅ 生成专业课程 {len(professional_courses)} 门")
        print(f"📊 总计生成课程 {len(courses)} 门")
        
        return courses

    def _generate_public_courses(self) -> List[Dict]:
        """生成公共课程"""
        courses = []
        
        for i, (name, category, credits) in enumerate(self.public_courses):
            # 为每个公共课创建多个班级（因为学生多）
            classes_count = random.randint(8, 15)  # 每门公共课开8-15个班
            
            for class_num in range(1, classes_count + 1):
                course_code = f"PUB{i+1:03d}_{class_num:02d}"
                display_name = f"{name}" if class_num == 1 else f"{name}({class_num}班)"
                
                course = {
                    'code': course_code,
                    'name': display_name,
                    'english_name': self._translate_to_english(name),
                    'credits': credits,
                    'hours': credits * 16,
                    'course_type': 'public',
                    'department': self._get_department_for_public_course(category),
                    'semester': random.choice([self.config.semester_fall, self.config.semester_spring]),
                    'academic_year': self.config.academic_year,
                    'description': f"{category}，{name}的基础课程",
                    'objectives': f"通过本课程学习，学生能够掌握{name}的基本理论和方法",
                    'max_students': random.randint(150, 300),  # 公共课人数多
                    'min_students': 100,
                    'is_active': True,
                    'is_published': True
                }
                courses.append(course)
        
        return courses

    def _generate_professional_courses(self, target_count: int, existing_codes: Set[str]) -> List[Dict]:
        """生成专业课程"""
        courses = []
        course_counter = 1
        
        # 计算每个院系应该生成的课程数量
        dept_names = list(self.departments.keys())
        courses_per_dept = target_count // len(dept_names)
        
        for dept_name, dept_info in self.departments.items():
            print(f"  📖 生成 {dept_name} 课程...")
            
            dept_courses = []
            
            # 为该院系的每个专业生成课程
            for major in dept_info['majors']:
                major_courses = self._generate_major_courses(
                    dept_name, major, dept_info['course_categories'], 
                    courses_per_dept // len(dept_info['majors']),
                    course_counter, existing_codes
                )
                dept_courses.extend(major_courses)
                course_counter += len(major_courses)
            
            courses.extend(dept_courses)
            print(f"    ✅ {dept_name} 生成 {len(dept_courses)} 门课程")
        
        return courses

    def _generate_major_courses(self, dept_name: str, major: str, 
                               categories: List[str], target_count: int,
                               start_counter: int, existing_codes: Set[str]) -> List[Dict]:
        """为特定专业生成课程"""
        courses = []
        
        for i in range(target_count):
            # 选择课程类型
            course_type = random.choices(
                list(self.course_types.keys()),
                weights=[config['weight'] for config in self.course_types.values()]
            )[0]
            
            type_config = self.course_types[course_type]
            
            # 生成课程基本信息
            credits = random.randint(*type_config['credits_range'])
            hours = credits * type_config['hours_multiplier']
            max_students = random.randint(*type_config['max_students_range'])
            
            # 选择课程类别和名称
            category = random.choice(categories)
            course_templates = self.course_templates.get(category, [f"{category}基础"])
            base_name = random.choice(course_templates)
            
            # 生成唯一课程代码
            course_code = self._generate_unique_code(dept_name, start_counter + i, existing_codes)
            existing_codes.add(course_code)
            
            # 添加级别标识
            level_suffix = self._get_course_level_suffix(course_type, i)
            full_name = f"{base_name}{level_suffix}"
            
            course = {
                'code': course_code,
                'name': full_name,
                'english_name': self._translate_to_english(base_name),
                'credits': credits,
                'hours': hours,
                'course_type': course_type,
                'department': dept_name,
                'semester': random.choice([self.config.semester_fall, self.config.semester_spring]),
                'academic_year': self.config.academic_year,
                'description': f"{major}专业{course_type}课程，{category}方向",
                'objectives': f"培养学生在{category}领域的专业能力",
                'max_students': max_students,
                'min_students': max(10, max_students // 5),
                'is_active': True,
                'is_published': True
            }
            
            courses.append(course)
        
        return courses

    def _generate_unique_code(self, dept_name: str, counter: int, existing_codes: Set[str]) -> str:
        """生成唯一的课程代码"""
        # 根据院系名称生成代码前缀
        dept_prefixes = {
            "计算机学院": "CS",
            "数学学院": "MATH",
            "物理学院": "PHYS",
            "化学学院": "CHEM",
            "生物学院": "BIO",
            "外国语学院": "FL",
            "经济管理学院": "ECON",
            "文学院": "LIT",
            "艺术学院": "ART",
            "体育学院": "PE",
            "医学院": "MED",
            "法学院": "LAW",
            "教育学院": "EDU",
            "工学院": "ENG",
            "材料学院": "MAT"
        }
        
        prefix = dept_prefixes.get(dept_name, "GEN")
        
        # 生成唯一代码
        attempt = 0
        while True:
            code = f"{prefix}{counter + attempt:04d}"
            if code not in existing_codes:
                return code
            attempt += 1

    def _get_course_level_suffix(self, course_type: str, index: int) -> str:
        """获取课程级别后缀"""
        if course_type == 'required':
            levels = ["", "(基础)", "(进阶)", "(高级)"]
        elif course_type == 'professional':
            levels = ["", "(专业基础)", "(专业核心)", "(专业选修)"]
        else:
            levels = ["", "(一)", "(二)", "(三)"]
        
        return levels[index % len(levels)]

    def _get_department_for_public_course(self, category: str) -> str:
        """为公共课程分配院系"""
        mapping = {
            "思政课": "马克思主义学院",
            "外语课": "外国语学院", 
            "体育课": "体育学院",
            "军事课": "学生工作部",
            "素质课": "教育学院",
            "计算机课": "计算机学院",
            "数学课": "数学学院"
        }
        return mapping.get(category, "教务处")

    def _translate_to_english(self, chinese_name: str) -> str:
        """简单的中英文对照翻译"""
        translations = {
            "程序设计": "Programming",
            "数据结构": "Data Structures",
            "算法": "Algorithms",
            "数据库": "Database",
            "网络": "Network",
            "人工智能": "Artificial Intelligence",
            "机器学习": "Machine Learning",
            "高等数学": "Advanced Mathematics",
            "线性代数": "Linear Algebra",
            "概率统计": "Probability and Statistics",
            "大学物理": "College Physics",
            "无机化学": "Inorganic Chemistry",
            "有机化学": "Organic Chemistry",
            "英语": "English",
            "思想道德修养": "Moral Education",
            "马克思主义": "Marxism",
            "体育": "Physical Education"
        }
        
        for chinese, english in translations.items():
            if chinese in chinese_name:
                return english
        
        return "Course"

class CourseDatabase:
    """课程数据库操作管理器"""
    
    def __init__(self, config: CourseGenerationConfig):
        self.config = config

    def save_courses(self, courses: List[Dict]) -> int:
        """保存课程数据到数据库"""
        print("💾 保存课程数据到数据库...")
        
        created_count = 0
        batch = []
        total_courses = len(courses)
        
        # 获取现有教师（用于随机分配）
        teachers = list(User.objects.filter(user_type='teacher', is_active=True))
        if not teachers:
            print("⚠️  警告：没有找到教师数据，课程将不分配教师")
        
        for i, course_data in enumerate(courses):
            if i % 100 == 0:
                print(f"\r保存课程进度: {i+1}/{total_courses} ({(i+1)/total_courses*100:.1f}%)", end="")
            
            # 检查课程是否已存在
            if Course.objects.filter(code=course_data['code']).exists():
                continue
            
            try:
                course = Course(
                    code=course_data['code'],
                    name=course_data['name'],
                    english_name=course_data['english_name'],
                    credits=course_data['credits'],
                    hours=course_data['hours'],
                    course_type=course_data['course_type'],
                    department=course_data['department'],
                    semester=course_data['semester'],
                    academic_year=course_data['academic_year'],
                    description=course_data['description'],
                    objectives=course_data['objectives'],
                    max_students=course_data['max_students'],
                    min_students=course_data['min_students'],
                    is_active=course_data['is_active'],
                    is_published=course_data['is_published']
                )
                batch.append(course)
                created_count += 1
                
                # 批量保存
                if len(batch) >= self.config.batch_size:
                    Course.objects.bulk_create(batch, ignore_conflicts=True)
                    
                    # 为新创建的课程分配教师
                    if teachers:
                        self._assign_teachers_to_batch(batch, teachers)
                    
                    batch = []
                    
            except Exception as e:
                print(f"\n⚠️  跳过课程 {course_data['code']}: {e}")
                continue
        
        # 保存剩余的课程
        if batch:
            Course.objects.bulk_create(batch, ignore_conflicts=True)
            if teachers:
                self._assign_teachers_to_batch(batch, teachers)
        
        print(f"\n✅ 课程保存完成：新增 {created_count} 门课程")
        return created_count

    def _assign_teachers_to_batch(self, courses: List[Course], teachers: List[User]):
        """为批量课程分配教师"""
        for course in courses:
            try:
                # 为每门课程随机分配1-3名教师
                num_teachers = random.randint(1, min(3, len(teachers)))
                assigned_teachers = random.sample(teachers, num_teachers)
                
                # 获取实际保存的课程对象
                saved_course = Course.objects.get(code=course.code)
                saved_course.teachers.set(assigned_teachers)
                
            except Course.DoesNotExist:
                continue
            except Exception as e:
                print(f"\n⚠️  教师分配失败 {course.code}: {e}")
                continue

def main():
    """主函数"""
    print("📚 智能课程数据生成器启动")
    print("=" * 60)
    
    # 检查当前数据状况
    current_students = User.objects.filter(user_type='student').count()
    current_teachers = User.objects.filter(user_type='teacher').count()
    current_courses = Course.objects.count()
    current_classrooms = Classroom.objects.count()
    
    print(f"📊 当前数据状况：")
    print(f"   学生数量: {current_students:,}")
    print(f"   教师数量: {current_teachers:,}")
    print(f"   课程数量: {current_courses:,}")
    print(f"   教室数量: {current_classrooms:,}")
    print()
    
    if current_teachers == 0:
        print("❌ 错误：数据库中没有教师数据，请先确保有教师数据")
        return
    
    if current_classrooms < 1000:
        print("❌ 错误：教室数量不足，请先运行教室数据生成器")
        return
    
    # 初始化配置
    config = CourseGenerationConfig()
    generator = IntelligentCourseGenerator(config)
    db_manager = CourseDatabase(config)
    
    start_time = datetime.now()
    
    try:
        # 生成课程数据
        print("📚 开始生成课程数据...")
        courses = generator.generate_courses()
        
        # 保存到数据库
        created_count = db_manager.save_courses(courses)
        
        # 计算用时
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 课程数据生成完成！")
        print(f"⏱️  总用时: {duration}")
        print(f"📚 新增课程: {created_count} 门")
        print(f"📊 课程总数: {Course.objects.count()} 门")
        print()
        print("📋 下一步：运行排课数据生成器")
        print("   python intelligent_schedule_generator.py")
        
    except Exception as e:
        print(f"❌ 生成过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()