#!/usr/bin/env python
"""
测试运行脚本
用于运行课程管理系统的所有测试
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """设置Django环境"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_settings')
    django.setup()

def run_tests(test_labels=None, verbosity=2, interactive=False):
    """运行测试"""
    setup_django()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity, interactive=interactive)
    
    if test_labels is None:
        # 运行所有应用的测试
        test_labels = [
            'apps.users.tests',
            'apps.courses.tests',
            'apps.classrooms.tests',
            'apps.schedules.tests',
            'apps.analytics.tests',
            'apps.notifications.tests',
            'apps.files.tests',
            'apps.students.tests',
            'apps.teachers.tests',
            'apps.algorithms.tests',
        ]
    
    failures = test_runner.run_tests(test_labels)
    
    if failures:
        print(f"\n❌ 测试失败: {failures} 个测试用例失败")
        return False
    else:
        print("\n✅ 所有测试通过!")
        return True

def run_specific_app_tests(app_name, verbosity=2):
    """运行特定应用的测试"""
    test_label = f'apps.{app_name}.tests'
    print(f"运行 {app_name} 应用的测试...")
    return run_tests([test_label], verbosity=verbosity)

def run_coverage_tests():
    """运行带覆盖率的测试"""
    try:
        import coverage
    except ImportError:
        print("❌ 需要安装 coverage 包: pip install coverage")
        return False
    
    print("运行带覆盖率的测试...")
    
    # 启动覆盖率测量
    cov = coverage.Coverage()
    cov.start()
    
    # 运行测试
    success = run_tests(verbosity=1)
    
    # 停止覆盖率测量
    cov.stop()
    cov.save()
    
    # 生成报告
    print("\n" + "="*50)
    print("测试覆盖率报告:")
    print("="*50)
    cov.report()
    
    # 生成HTML报告
    try:
        cov.html_report(directory='htmlcov')
        print(f"\nHTML覆盖率报告已生成: htmlcov/index.html")
    except Exception as e:
        print(f"生成HTML报告失败: {e}")
    
    return success

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='运行课程管理系统测试')
    parser.add_argument(
        '--app', 
        help='运行特定应用的测试 (users, courses, schedules, etc.)'
    )
    parser.add_argument(
        '--coverage', 
        action='store_true',
        help='运行带覆盖率的测试'
    )
    parser.add_argument(
        '--verbosity', 
        type=int, 
        default=2,
        help='测试输出详细程度 (0-3)'
    )
    parser.add_argument(
        'test_labels', 
        nargs='*',
        help='特定的测试标签'
    )
    
    args = parser.parse_args()
    
    print("🧪 课程管理系统测试运行器")
    print("="*50)
    
    try:
        if args.coverage:
            success = run_coverage_tests()
        elif args.app:
            success = run_specific_app_tests(args.app, args.verbosity)
        else:
            success = run_tests(args.test_labels or None, args.verbosity)
        
        if success:
            print("\n🎉 测试运行完成!")
            sys.exit(0)
        else:
            print("\n💥 测试运行失败!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试运行出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
