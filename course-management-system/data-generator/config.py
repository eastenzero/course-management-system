# file: data-generator/config.py
# 功能: 数据生成配置文件

from typing import Dict, List, Any
from dataclasses import dataclass

# 数据规模配置
DATA_SCALE_CONFIG = {
    'large': {
        'students': 25000,        # 学生总数
        'teachers': 1500,         # 教师总数
        'courses': 3000,          # 课程总数
        'classrooms': 300,        # 教室总数
        'departments': 20,        # 院系数量
        'majors': 80,            # 专业数量
        'semesters': 8,          # 学期数量
        'time_slots': 12,        # 每日时间段数
        'weeks_per_semester': 18, # 每学期周数
    },
    'medium': {
        'students': 12000,
        'teachers': 800,
        'courses': 1500,
        'classrooms': 150,
        'departments': 12,
        'majors': 40,
        'semesters': 8,
        'time_slots': 10,
        'weeks_per_semester': 16,
    },
    'small': {
        'students': 5000,
        'teachers': 300,
        'courses': 600,
        'classrooms': 60,
        'departments': 6,
        'majors': 20,
        'semesters': 8,
        'time_slots': 8,
        'weeks_per_semester': 16,
    }
}

# 院系专业配置
DEPARTMENT_CONFIG = {
    'templates': [
        "计算机科学与技术学院", "软件学院", "信息工程学院",
        "电子信息工程学院", "机械工程学院", "材料科学与工程学院",
        "化学化工学院", "生物科学学院", "数学与统计学院",
        "物理学院", "经济管理学院", "工商管理学院",
        "外国语学院", "文学院", "法学院",
        "医学院", "护理学院", "药学院",
        "建筑学院", "土木工程学院"
    ],
    'major_mapping': {
        "计算机科学与技术学院": [
            "计算机科学与技术", "软件工程", "网络工程", 
            "信息安全", "数据科学与大数据技术", "人工智能"
        ],
        "电子信息工程学院": [
            "电子信息工程", "通信工程", "电子科学与技术",
            "微电子科学与工程", "光电信息科学与工程"
        ],
        "机械工程学院": [
            "机械设计制造及其自动化", "机械电子工程", "车辆工程",
            "工业设计", "过程装备与控制工程"
        ],
        "经济管理学院": [
            "工商管理", "市场营销", "会计学", "财务管理",
            "人力资源管理", "国际经济与贸易", "金融学"
        ],
        "医学院": [
            "临床医学", "口腔医学", "预防医学", "医学影像学",
            "麻醉学", "精神医学"
        ]
    }
}

# 用户配置
USER_CONFIG = {
    'surnames': ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
                '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗'],
    'given_names': ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
                   '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞'],
    'teacher_titles': ['教授', '副教授', '讲师', '助教'],
    'teacher_title_weights': [0.15, 0.25, 0.45, 0.15],
    'degrees': ['博士', '硕士', '学士'],
    'degree_weights': [0.7, 0.25, 0.05],
    'student_status': ['在读', '休学', '毕业'],
    'student_status_weights': [0.9, 0.05, 0.05],
    'teacher_status': ['在职', '退休', '离职'],
    'teacher_status_weights': [0.9, 0.08, 0.02]
}

# 课程配置
COURSE_CONFIG = {
    'templates': {
        "计算机": [
            "数据结构与算法", "计算机网络", "操作系统", "数据库系统",
            "软件工程", "编译原理", "计算机组成原理", "人工智能导论",
            "机器学习", "深度学习", "计算机图形学", "网络安全",
            "分布式系统", "云计算技术", "大数据处理", "区块链技术"
        ],
        "数学": [
            "高等数学", "线性代数", "概率论与数理统计", "离散数学",
            "数值分析", "运筹学", "数学建模", "复变函数",
            "实变函数", "泛函分析", "微分方程", "拓扑学"
        ],
        "物理": [
            "大学物理", "理论力学", "电磁学", "热力学与统计物理",
            "量子力学", "固体物理", "光学", "原子物理学",
            "核物理", "粒子物理", "天体物理", "凝聚态物理"
        ],
        "化学": [
            "无机化学", "有机化学", "物理化学", "分析化学",
            "生物化学", "高分子化学", "材料化学", "环境化学",
            "药物化学", "化工原理", "化学工程", "催化化学"
        ],
        "经济": [
            "微观经济学", "宏观经济学", "计量经济学", "国际经济学",
            "货币银行学", "财政学", "投资学", "公司金融",
            "证券投资", "期货与期权", "风险管理", "行为金融学"
        ],
        "管理": [
            "管理学原理", "组织行为学", "人力资源管理", "市场营销",
            "战略管理", "运营管理", "项目管理", "质量管理",
            "供应链管理", "创新管理", "领导力", "企业文化"
        ]
    },
    'types': ['必修', '选修', '限选', '通识'],
    'type_weights': [0.4, 0.3, 0.2, 0.1],
    'credit_options': [1, 2, 3, 4, 5],
    'credit_weights': [0.1, 0.2, 0.4, 0.25, 0.05],
    'assessment_methods': ['考试', '考查', '论文', '项目']
}

# 设施配置
FACILITY_CONFIG = {
    'building_names': [
        "文科楼", "理科楼", "工科楼", "实验楼", "图书馆",
        "行政楼", "学生活动中心", "体育馆", "艺术楼", "医学楼"
    ],
    'room_types': {
        "普通教室": {"capacity_range": (30, 150), "equipment": ["投影仪", "音响", "黑板"]},
        "多媒体教室": {"capacity_range": (50, 200), "equipment": ["投影仪", "音响", "电脑", "网络"]},
        "实验室": {"capacity_range": (20, 40), "equipment": ["实验台", "仪器设备", "通风系统"]},
        "机房": {"capacity_range": (30, 60), "equipment": ["电脑", "网络", "投影仪", "空调"]},
        "阶梯教室": {"capacity_range": (100, 500), "equipment": ["投影仪", "音响", "话筒", "灯光"]},
        "研讨室": {"capacity_range": (10, 30), "equipment": ["白板", "投影仪", "圆桌"]}
    },
    'time_slots': [
        {"name": "第1节", "start": "08:00", "end": "08:45"},
        {"name": "第2节", "start": "08:55", "end": "09:40"},
        {"name": "第3节", "start": "10:00", "end": "10:45"},
        {"name": "第4节", "start": "10:55", "end": "11:40"},
        {"name": "第5节", "start": "14:00", "end": "14:45"},
        {"name": "第6节", "start": "14:55", "end": "15:40"},
        {"name": "第7节", "start": "16:00", "end": "16:45"},
        {"name": "第8节", "start": "16:55", "end": "17:40"},
        {"name": "第9节", "start": "19:00", "end": "19:45"},
        {"name": "第10节", "start": "19:55", "end": "20:40"},
    ]
}

# 输出配置
OUTPUT_CONFIG = {
    'json_dir': 'output/json',
    'sql_dir': 'output/sql',
    'reports_dir': 'output/reports',
    'encoding': 'utf-8',
    'indent': 2
}

# 验证配置
VALIDATION_CONFIG = {
    'max_errors_per_type': 100,
    'required_fields': {
        'departments': ['id', 'name', 'code'],
        'majors': ['id', 'name', 'department_id'],
        'students': ['id', 'student_id', 'name', 'major_id'],
        'teachers': ['id', 'employee_id', 'name', 'department_id'],
        'courses': ['id', 'code', 'name', 'department_id'],
        'classrooms': ['id', 'building', 'room_number', 'capacity'],
    }
}

@dataclass
class GenerationConfig:
    """数据生成配置类"""
    scale: str
    output_format: List[str] = None
    output_dir: str = 'output'
    validate_data: bool = True
    include_conflicts: bool = True
    
    def __post_init__(self):
        if self.output_format is None:
            self.output_format = ['json', 'sql']
        
        if self.scale not in DATA_SCALE_CONFIG:
            raise ValueError(f"不支持的数据规模: {self.scale}")
    
    @property
    def scale_config(self) -> Dict[str, int]:
        """获取规模配置"""
        return DATA_SCALE_CONFIG[self.scale]
