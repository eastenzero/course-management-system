# file: data-generator/__init__.py
# 功能: 数据生成模块初始化

"""
校园课程表管理系统 - 测试数据生成模块

这个模块提供了完整的测试数据生成功能，包括：
- 院系专业数据生成
- 用户数据生成（学生、教师）
- 课程数据生成
- 设施时间数据生成
- 复杂场景数据生成
- 数据导出和验证

使用示例:
    from data_generator import generate_complete_dataset
    
    # 生成大规模测试数据
    dataset = generate_complete_dataset('large')
    
    # 生成并导出数据
    from data_generator.main import main
    main(['--scale', 'medium', '--format', 'json', 'sql'])
"""

__version__ = "1.0.0"
__author__ = "Course Management System Team"
__email__ = "dev@university.edu.cn"

# 导入主要功能
from .config import (
    DATA_SCALE_CONFIG,
    DEPARTMENT_CONFIG,
    USER_CONFIG,
    COURSE_CONFIG,
    FACILITY_CONFIG,
    GenerationConfig
)

# 导入生成器
from .generators import (
    DepartmentGenerator,
    UserGenerator,
    CourseGenerator,
    FacilityGenerator,
    ComplexScenarioGenerator,
    DataExporter
)

# 导入主生成函数
from .main import generate_complete_dataset

__all__ = [
    # 配置
    'DATA_SCALE_CONFIG',
    'DEPARTMENT_CONFIG', 
    'USER_CONFIG',
    'COURSE_CONFIG',
    'FACILITY_CONFIG',
    'GenerationConfig',
    
    # 生成器
    'DepartmentGenerator',
    'UserGenerator',
    'CourseGenerator',
    'FacilityGenerator',
    'ComplexScenarioGenerator',
    'DataExporter',
    
    # 主函数
    'generate_complete_dataset'
]
