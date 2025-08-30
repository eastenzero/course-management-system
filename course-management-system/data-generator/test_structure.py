# file: data-generator/test_structure.py
# 功能: 测试代码结构和导入

"""
简单的结构测试脚本，验证所有模块是否可以正确导入
"""

import sys
from pathlib import Path

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        # 测试配置模块
        print("  ✓ 导入配置模块...")
        from config import DATA_SCALE_CONFIG, DEPARTMENT_CONFIG
        print(f"    - 支持的数据规模: {list(DATA_SCALE_CONFIG.keys())}")
        
        # 测试生成器模块（如果faker可用）
        try:
            print("  ✓ 导入生成器模块...")
            from generators import (
                DepartmentGenerator,
                UserGenerator,
                CourseGenerator,
                FacilityGenerator,
                ComplexScenarioGenerator,
                DataExporter
            )
            print("    - 所有生成器导入成功")
            
            # 测试主模块
            print("  ✓ 导入主模块...")
            from main import generate_complete_dataset
            print("    - 主生成函数导入成功")
            
            return True
            
        except ImportError as e:
            print(f"  ⚠️  生成器模块导入失败: {e}")
            print("    - 可能缺少依赖包，请运行: pip install -r requirements.txt")
            return False
            
    except Exception as e:
        print(f"  ❌ 导入失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n测试文件结构...")
    
    base_dir = Path(__file__).parent
    
    required_files = [
        'config.py',
        'main.py',
        'requirements.txt',
        'README.md',
        'generators/__init__.py',
        'generators/department.py',
        'generators/user.py',
        'generators/course.py',
        'generators/facility.py',
        'generators/scenario.py',
        'generators/exporter.py',
        'tests/__init__.py',
        'tests/test_generators.py',
        'tests/test_data_quality.py',
        'examples.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ❌ {file_path} (缺失)")
            missing_files.append(file_path)
    
    required_dirs = [
        'generators',
        'tests',
        'output',
        'output/json',
        'output/sql',
        'output/reports'
    ]
    
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"  ✓ {dir_path}/ (目录)")
        else:
            print(f"  ❌ {dir_path}/ (目录缺失)")
            missing_files.append(dir_path)
    
    return len(missing_files) == 0

def test_configuration():
    """测试配置"""
    print("\n测试配置...")
    
    try:
        from config import DATA_SCALE_CONFIG, DEPARTMENT_CONFIG, USER_CONFIG, COURSE_CONFIG
        
        # 检查数据规模配置
        for scale, config in DATA_SCALE_CONFIG.items():
            print(f"  ✓ {scale} 规模配置:")
            print(f"    - 学生: {config['students']:,}")
            print(f"    - 教师: {config['teachers']:,}")
            print(f"    - 课程: {config['courses']:,}")
            print(f"    - 教室: {config['classrooms']:,}")
        
        # 检查院系配置
        dept_count = len(DEPARTMENT_CONFIG['templates'])
        print(f"  ✓ 院系模板: {dept_count} 个")
        
        # 检查用户配置
        surname_count = len(USER_CONFIG['surnames'])
        print(f"  ✓ 姓氏库: {surname_count} 个")
        
        # 检查课程配置
        course_categories = len(COURSE_CONFIG['templates'])
        print(f"  ✓ 课程类别: {course_categories} 个")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 数据生成器结构测试")
    print("=" * 50)
    
    # 运行测试
    structure_ok = test_file_structure()
    config_ok = test_configuration()
    import_ok = test_imports()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"  文件结构: {'✓ 通过' if structure_ok else '❌ 失败'}")
    print(f"  配置测试: {'✓ 通过' if config_ok else '❌ 失败'}")
    print(f"  模块导入: {'✓ 通过' if import_ok else '❌ 失败'}")
    
    if all([structure_ok, config_ok, import_ok]):
        print("\n🎉 所有测试通过！数据生成器结构正确。")
        print("\n📝 下一步:")
        print("  1. 安装依赖: pip install -r requirements.txt")
        print("  2. 运行生成器: python main.py --scale small")
        print("  3. 查看示例: python examples.py")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查上述问题。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
