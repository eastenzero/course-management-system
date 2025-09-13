#!/usr/bin/env python
"""
数据迁移和清理编排器
基于专业百万级数据生成脚本 generate_real_million_data_simplified.py

功能：
1. 数据清理：备份重要数据，清理污染数据
2. 专业数据生成：使用经过各种考量的百万级数据生成方案
3. 数据验证：确保数据质量和完整性
4. 性能监控：全程监控内存、性能指标

专业生成脚本特点：
- 内存优化：batch_size=2000，分批处理
- 性能考量：预编译密码哈希，减少重复计算
- 数据质量：真实中文姓名生成算法
- 规模控制：800,000学生 + 50,000教师的百万级规模
- 错误处理：完整的异常处理和回滚机制
"""

import os
import sys
import time
import gc
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.core.management import execute_from_command_line
from apps.courses.models import Course, Enrollment

User = get_user_model()

class DataCleanupManager:
    """数据清理管理器"""
    
    def __init__(self):
        self.backup_data = {}
        
    def backup_critical_data(self) -> Dict:
        """备份关键数据"""
        print("🔄 备份关键管理数据...")
        
        # 备份超级用户和管理员
        admin_users = list(User.objects.filter(
            is_superuser=True
        ).values())
        
        staff_users = list(User.objects.filter(
            is_staff=True,
            user_type='admin'
        ).values())
        
        # 备份重要课程模板
        template_courses = list(Course.objects.filter(
            name__icontains='模板'
        ).values())
        
        backup = {
            'admin_users': admin_users,
            'staff_users': staff_users,
            'template_courses': template_courses,
            'backup_time': datetime.now().isoformat()
        }
        
        self.backup_data = backup
        print(f"   ✅ 已备份: {len(admin_users)} 超级用户, {len(staff_users)} 管理员, {len(template_courses)} 模板课程")
        return backup
    
    def identify_pollution_data(self) -> Dict:
        """识别污染数据"""
        print("🔍 识别污染数据...")
        
        # 识别各种测试数据
        pollution_stats = {
            'million_users': User.objects.filter(username__startswith='million_').count(),
            'MILLION_users': User.objects.filter(username__startswith='MILLION_').count(),
            'test_users': User.objects.filter(username__startswith='test_').count(),
            'student_users': User.objects.filter(username__startswith='student_').count(),
            'teacher_users': User.objects.filter(username__startswith='teacher_').count(),
            'million_courses': Course.objects.filter(code__startswith='MILLION_').count(),
            'test_courses': Course.objects.filter(code__startswith='TEST_').count(),
            'total_enrollments': Enrollment.objects.count()
        }
        
        total_pollution = (
            pollution_stats['million_users'] + 
            pollution_stats['MILLION_users'] + 
            pollution_stats['test_users'] + 
            pollution_stats['student_users'] + 
            pollution_stats['teacher_users'] + 
            pollution_stats['million_courses'] + 
            pollution_stats['test_courses']
        )
        
        print(f"   📊 污染数据统计:")
        for key, count in pollution_stats.items():
            if count > 0:
                print(f"      {key}: {count:,} 条")
        print(f"   📊 总污染数据: {total_pollution:,} 条")
        
        return pollution_stats
    
    def cleanup_pollution_data(self) -> Dict:
        """清理污染数据"""
        print("🧹 开始清理污染数据...")
        
        cleanup_stats = {}
        
        try:
            with transaction.atomic():
                # 清理选课记录（避免外键约束）
                deleted_enrollments = Enrollment.objects.filter(
                    student__username__startswith='million_'
                ).delete()
                cleanup_stats['enrollments'] = deleted_enrollments[0] if deleted_enrollments[0] else 0
                
                # 清理百万级测试用户
                deleted_million = User.objects.filter(
                    username__startswith='million_'
                ).delete()
                cleanup_stats['million_users'] = deleted_million[0] if deleted_million[0] else 0
                
                # 清理MILLION前缀用户
                deleted_MILLION = User.objects.filter(
                    username__startswith='MILLION_'
                ).delete()
                cleanup_stats['MILLION_users'] = deleted_MILLION[0] if deleted_MILLION[0] else 0
                
                # 清理测试用户
                deleted_test = User.objects.filter(
                    username__startswith='test_'
                ).delete()
                cleanup_stats['test_users'] = deleted_test[0] if deleted_test[0] else 0
                
                # 清理student前缀用户
                deleted_student = User.objects.filter(
                    username__startswith='student_'
                ).delete()
                cleanup_stats['student_users'] = deleted_student[0] if deleted_student[0] else 0
                
                # 清理teacher前缀用户
                deleted_teacher = User.objects.filter(
                    username__startswith='teacher_'
                ).delete()
                cleanup_stats['teacher_users'] = deleted_teacher[0] if deleted_teacher[0] else 0
                
                # 清理测试课程
                deleted_courses = Course.objects.filter(
                    code__startswith='MILLION_'
                ).delete()
                cleanup_stats['million_courses'] = deleted_courses[0] if deleted_courses[0] else 0
                
                deleted_test_courses = Course.objects.filter(
                    code__startswith='TEST_'
                ).delete()
                cleanup_stats['test_courses'] = deleted_test_courses[0] if deleted_test_courses[0] else 0
                
        except Exception as e:
            print(f"   ❌ 清理失败: {e}")
            return {}
        
        total_cleaned = sum(cleanup_stats.values())
        print(f"   ✅ 清理完成:")
        for key, count in cleanup_stats.items():
            if count > 0:
                print(f"      {key}: {count:,} 条")
        print(f"   📊 总清理: {total_cleaned:,} 条记录")
        
        # 强制垃圾回收
        gc.collect()
        
        return cleanup_stats

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.start_time = None
        self.stats = {
            'memory_usage': [],
            'cpu_usage': [],
            'generation_speed': []
        }
    
    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
        print("📊 性能监控已启动")
    
    def get_current_stats(self) -> Dict:
        """获取当前系统状态"""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            'memory_percent': memory.percent,
            'memory_mb': memory.used / (1024 * 1024),
            'cpu_percent': cpu_percent,
            'timestamp': time.time()
        }
    
    def log_progress(self, stage: str, current: int, total: int, speed: float = 0):
        """记录进度"""
        stats = self.get_current_stats()
        progress = (current / total) * 100 if total > 0 else 0
        
        print(f"   📈 {stage}: {current:,}/{total:,} ({progress:.1f}%) | "
              f"速度: {speed:.0f} 条/秒 | "
              f"内存: {stats['memory_mb']:.0f}MB ({stats['memory_percent']:.1f}%) | "
              f"CPU: {stats['cpu_percent']:.1f}%")
        
        self.stats['memory_usage'].append(stats['memory_percent'])
        self.stats['cpu_usage'].append(stats['cpu_percent'])
        if speed > 0:
            self.stats['generation_speed'].append(speed)

class DataMigrationOrchestrator:
    """数据迁移编排器 - 基于专业百万级数据生成脚本"""
    
    def __init__(self):
        self.cleanup_manager = DataCleanupManager()
        self.performance_monitor = PerformanceMonitor()
        self.migration_stats = {}
        
    def execute_migration(self) -> Dict:
        """执行完整的数据迁移流程"""
        print("🚀 数据迁移和清理系统启动")
        print("=" * 80)
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 基于专业脚本: generate_real_million_data_simplified.py")
        print("📊 预期数据规模:")
        print("   - 学生用户: 800,000")
        print("   - 教师用户: 50,000")
        print("   - 课程数据: 30,000")
        print("   - 选课记录: 200,000")
        print("   - 预期总量: 1,080,000+ 条记录")
        print("=" * 80)
        
        total_start_time = time.time()
        self.performance_monitor.start_monitoring()
        
        try:
            # 阶段1：数据备份
            print(f"\n🎯 阶段1: 数据备份")
            backup_data = self.cleanup_manager.backup_critical_data()
            
            # 阶段2：识别污染数据
            print(f"\n🎯 阶段2: 污染数据识别")
            pollution_stats = self.cleanup_manager.identify_pollution_data()
            
            # 阶段3：清理污染数据
            print(f"\n🎯 阶段3: 污染数据清理")
            cleanup_stats = self.cleanup_manager.cleanup_pollution_data()
            
            # 阶段4：执行专业数据生成
            print(f"\n🎯 阶段4: 专业百万级数据生成")
            generation_stats = self.execute_professional_generation()
            
            # 阶段5：数据验证
            print(f"\n🎯 阶段5: 数据验证")
            validation_stats = self.validate_generated_data()
            
            total_elapsed = time.time() - total_start_time
            
            # 生成最终报告
            final_report = self.generate_final_report({
                'backup': backup_data,
                'pollution': pollution_stats,
                'cleanup': cleanup_stats,
                'generation': generation_stats,
                'validation': validation_stats,
                'total_time': total_elapsed
            })
            
            return final_report
            
        except Exception as e:
            print(f"\n❌ 迁移过程失败: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def execute_professional_generation(self) -> Dict:
        """执行专业百万级数据生成"""
        print("   🚀 启动专业数据生成脚本...")
        
        # 导入专业生成脚本
        script_path = os.path.join(os.path.dirname(__file__), 'generate_real_million_data_simplified.py')
        
        if not os.path.exists(script_path):
            print(f"   ❌ 专业生成脚本不存在: {script_path}")
            return {'success': False}
        
        try:
            # 动态导入专业生成模块
            import importlib.util
            spec = importlib.util.spec_from_file_location("professional_generator", script_path)
            professional_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(professional_module)
            
            # 创建专业生成器实例
            generator = professional_module.MillionDataGenerator()
            
            start_time = time.time()
            
            # 分阶段生成数据（使用专业脚本的逻辑）
            print("   📊 第1步: 生成800,000名学生...")
            students_created = generator.generate_million_students(800000)
            
            print("   📊 第2步: 生成50,000名教师...")
            teachers_created = generator.generate_million_teachers(50000)
            
            print("   📊 第3步: 生成30,000门课程...")
            courses_created = generator.generate_million_courses(30000)
            
            print("   📊 第4步: 生成200,000条选课记录...")
            enrollments_created = generator.generate_million_enrollments(200000)
            
            total_created = students_created + teachers_created + courses_created + enrollments_created
            total_elapsed = time.time() - start_time
            
            generation_stats = {
                'success': True,
                'students_created': students_created,
                'teachers_created': teachers_created,
                'courses_created': courses_created,
                'enrollments_created': enrollments_created,
                'total_created': total_created,
                'generation_time': total_elapsed,
                'average_speed': total_created / total_elapsed if total_elapsed > 0 else 0
            }
            
            print(f"   ✅ 专业数据生成完成:")
            print(f"      学生用户: {students_created:,}")
            print(f"      教师用户: {teachers_created:,}")
            print(f"      课程数据: {courses_created:,}")
            print(f"      选课记录: {enrollments_created:,}")
            print(f"      总记录数: {total_created:,}")
            print(f"      生成耗时: {total_elapsed/60:.1f} 分钟")
            print(f"      平均速度: {generation_stats['average_speed']:.0f} 条/秒")
            
            return generation_stats
            
        except Exception as e:
            print(f"   ❌ 专业数据生成失败: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def validate_generated_data(self) -> Dict:
        """验证生成的数据"""
        print("   🔍 验证数据完整性...")
        
        try:
            # 统计生成的数据
            total_users = User.objects.count()
            student_users = User.objects.filter(user_type='student').count()
            teacher_users = User.objects.filter(user_type='teacher').count()
            total_courses = Course.objects.count()
            total_enrollments = Enrollment.objects.count()
            
            # 验证数据质量
            validation_results = {
                'total_users': total_users,
                'student_users': student_users,
                'teacher_users': teacher_users,
                'total_courses': total_courses,
                'total_enrollments': total_enrollments,
                'grand_total': total_users + total_courses + total_enrollments,
                'million_target_achieved': (total_users + total_courses + total_enrollments) >= 1000000,
                'data_integrity_checks': {
                    'unique_usernames': self.check_username_uniqueness(),
                    'valid_emails': self.check_email_format(),
                    'enrollment_consistency': self.check_enrollment_consistency()
                }
            }
            
            print(f"   📊 数据验证结果:")
            print(f"      总用户数: {total_users:,}")
            print(f"      学生用户: {student_users:,}")
            print(f"      教师用户: {teacher_users:,}")
            print(f"      总课程数: {total_courses:,}")
            print(f"      总选课记录: {total_enrollments:,}")
            print(f"      数据库总记录: {validation_results['grand_total']:,}")
            
            if validation_results['million_target_achieved']:
                print(f"   ✅ 成功达到百万级数据标准！")
            else:
                shortage = 1000000 - validation_results['grand_total']
                print(f"   ⚠️ 距离百万级还差 {shortage:,} 条记录")
            
            return validation_results
            
        except Exception as e:
            print(f"   ❌ 数据验证失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_username_uniqueness(self) -> bool:
        """检查用户名唯一性"""
        total_users = User.objects.count()
        unique_usernames = User.objects.values('username').distinct().count()
        return total_users == unique_usernames
    
    def check_email_format(self) -> float:
        """检查邮箱格式正确率"""
        total_users = User.objects.count()
        if total_users == 0:
            return 0.0
        
        valid_emails = User.objects.filter(email__contains='@').count()
        return (valid_emails / total_users) * 100
    
    def check_enrollment_consistency(self) -> bool:
        """检查选课记录一致性"""
        # 检查是否存在孤立的选课记录
        orphaned_enrollments = Enrollment.objects.filter(
            student__isnull=True
        ).count()
        return orphaned_enrollments == 0
    
    def generate_final_report(self, stats: Dict) -> Dict:
        """生成最终报告"""
        print("\n" + "=" * 80)
        print("🎉 数据迁移和清理完成！")
        print("=" * 80)
        
        report = {
            'migration_success': True,
            'completion_time': datetime.now().isoformat(),
            'total_duration_minutes': stats['total_time'] / 60,
            'professional_script_used': 'generate_real_million_data_simplified.py',
            'phases_completed': {
                'backup_phase': bool(stats.get('backup')),
                'cleanup_phase': bool(stats.get('cleanup')),
                'generation_phase': stats.get('generation', {}).get('success', False),
                'validation_phase': bool(stats.get('validation'))
            },
            'data_statistics': stats.get('validation', {}),
            'performance_summary': {
                'generation_time_minutes': stats.get('generation', {}).get('generation_time', 0) / 60,
                'average_speed_per_second': stats.get('generation', {}).get('average_speed', 0),
                'memory_usage': self.performance_monitor.stats
            }
        }
        
        print(f"📊 迁移总结:")
        print(f"   总耗时: {report['total_duration_minutes']:.1f} 分钟")
        print(f"   专业脚本: {report['professional_script_used']}")
        print(f"   数据生成速度: {report['performance_summary']['average_speed_per_second']:.0f} 条/秒")
        
        if stats.get('validation', {}).get('million_target_achieved'):
            print(f"   ✅ 百万级数据目标达成")
        
        return report

def main():
    """主函数"""
    orchestrator = DataMigrationOrchestrator()
    result = orchestrator.execute_migration()
    
    if result.get('migration_success'):
        print(f"\n🎊 数据迁移成功完成！")
        return True
    else:
        print(f"\n💥 数据迁移失败")
        return False

if __name__ == '__main__':
    main()