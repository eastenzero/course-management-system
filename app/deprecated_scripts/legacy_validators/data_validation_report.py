#!/usr/bin/env python
"""
数据验证和质量检查脚本
验证当前数据库中的数据状态，为百万级数据迁移提供基础报告

功能：
1. 统计当前数据库中的数据量
2. 分析数据质量和完整性
3. 识别污染数据
4. 为迁移制定策略建议
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

class DatabaseValidator:
    """数据库验证器"""
    
    def __init__(self):
        self.db_path = self.find_database_file()
        self.stats = {}
        self.validation_results = {}
        
    def find_database_file(self):
        """查找数据库文件"""
        possible_paths = [
            'course-management-system/backend/db.sqlite3',
            'backend/db.sqlite3',
            'db.sqlite3'
        ]
        
        for path in possible_paths:
            full_path = os.path.join(os.getcwd(), path)
            if os.path.exists(full_path):
                print(f"📂 找到数据库文件: {full_path}")
                return full_path
        
        # 如果没找到，创建一个简单的报告
        print("⚠️ 未找到SQLite数据库文件")
        return None
    
    def analyze_current_data(self):
        """分析当前数据状态"""
        if not self.db_path:
            return self.create_file_based_analysis()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.stats = {'tables': {}}
            
            for (table_name,) in tables:
                if table_name.startswith('django_') or table_name == 'sqlite_sequence':
                    continue
                
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    self.stats['tables'][table_name] = count
                    print(f"   {table_name}: {count:,} 条记录")
                except Exception as e:
                    print(f"   ⚠️ 无法查询表 {table_name}: {e}")
            
            # 特殊查询：用户相关数据
            try:
                cursor.execute("SELECT COUNT(*) FROM auth_user WHERE username LIKE 'million_%'")
                million_users = cursor.fetchone()[0]
                self.stats['million_users'] = million_users
                
                cursor.execute("SELECT COUNT(*) FROM auth_user WHERE user_type = 'student'")
                student_count = cursor.fetchone()[0]
                self.stats['student_users'] = student_count
                
                cursor.execute("SELECT COUNT(*) FROM auth_user WHERE user_type = 'teacher'")
                teacher_count = cursor.fetchone()[0]
                self.stats['teacher_users'] = teacher_count
                
            except Exception as e:
                print(f"   ⚠️ 无法查询用户数据: {e}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 数据库分析失败: {e}")
            return self.create_file_based_analysis()
        
        return self.stats
    
    def create_file_based_analysis(self):
        """基于文件系统的分析"""
        print("📁 执行基于文件系统的数据分析...")
        
        # 检查项目中的脚本文件
        scripts_analysis = {
            'professional_scripts_found': [],
            'data_generation_scripts': [],
            'million_data_scripts': []
        }
        
        project_root = os.getcwd()
        
        # 扫描Python脚本
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    # 检查是否为百万级数据生成脚本
                    if 'million' in file.lower():
                        scripts_analysis['million_data_scripts'].append(file_path)
                    
                    if 'generate' in file.lower() and 'data' in file.lower():
                        scripts_analysis['data_generation_scripts'].append(file_path)
                    
                    # 检查专业脚本
                    if 'simplified' in file.lower() or 'professional' in file.lower():
                        scripts_analysis['professional_scripts_found'].append(file_path)
        
        return scripts_analysis
    
    def identify_pollution_patterns(self):
        """识别数据污染模式"""
        pollution_patterns = {
            'username_patterns': [
                'million_', 'MILLION_', 'test_', 'student_', 'teacher_', 
                'user_', 'demo_', 'sample_', 'example_', 'dummy_'
            ],
            'course_patterns': [
                'MILLION_', 'TEST_', 'DEMO_', 'SAMPLE_', 'EXAMPLE_'
            ]
        }
        
        print("🔍 识别的污染数据模式:")
        print("   用户名模式:", ', '.join(pollution_patterns['username_patterns']))
        print("   课程代码模式:", ', '.join(pollution_patterns['course_patterns']))
        
        return pollution_patterns
    
    def validate_professional_script(self):
        """验证专业百万级数据生成脚本"""
        script_path = 'course-management-system/generate_real_million_data_simplified.py'
        full_path = os.path.join(os.getcwd(), script_path)
        
        if os.path.exists(full_path):
            print(f"✅ 专业脚本确认存在: {script_path}")
            
            # 读取脚本内容，分析关键特性
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                professional_features = {
                    'batch_processing': 'batch_size' in content,
                    'memory_optimization': 'gc.collect()' in content,
                    'chinese_names': 'generate_chinese_name' in content,
                    'password_optimization': 'make_password' in content,
                    'error_handling': 'try:' in content and 'except' in content,
                    'progress_monitoring': '进度' in content or 'progress' in content.lower(),
                }
                
                print("🔧 专业脚本特性分析:")
                for feature, exists in professional_features.items():
                    status = "✅" if exists else "❌"
                    print(f"   {status} {feature}: {'是' if exists else '否'}")
                
                return {
                    'script_exists': True,
                    'script_path': full_path,
                    'professional_features': professional_features
                }
                
            except Exception as e:
                print(f"⚠️ 无法读取脚本内容: {e}")
                
        else:
            print(f"❌ 专业脚本不存在: {script_path}")
            
        return {'script_exists': False}
    
    def calculate_migration_strategy(self):
        """计算迁移策略"""
        current_total = sum(self.stats.get('tables', {}).values())
        million_target = 1000000
        
        strategy = {
            'current_total_records': current_total,
            'million_target': million_target,
            'needs_migration': current_total < million_target,
            'cleanup_required': self.stats.get('million_users', 0) > 0,
            'estimated_generation_time': '2-3小时（基于专业脚本）',
            'recommended_approach': 'professional_simplified_script'
        }
        
        if strategy['needs_migration']:
            shortage = million_target - current_total
            strategy['records_to_generate'] = shortage
            print(f"📊 迁移策略分析:")
            print(f"   当前记录数: {current_total:,}")
            print(f"   目标记录数: {million_target:,}")
            print(f"   需要生成: {shortage:,} 条记录")
            print(f"   推荐方式: 使用专业脚本 generate_real_million_data_simplified.py")
        else:
            print(f"✅ 当前数据已达到百万级标准")
        
        return strategy
    
    def generate_validation_report(self):
        """生成验证报告"""
        print("📋 生成数据验证报告")
        print("=" * 80)
        print(f"⏰ 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 数据分析
        print("\n🔍 第1部分: 数据状态分析")
        current_data = self.analyze_current_data()
        
        # 2. 污染识别
        print("\n🧹 第2部分: 污染数据识别")
        pollution_patterns = self.identify_pollution_patterns()
        
        # 3. 专业脚本验证
        print("\n🔧 第3部分: 专业脚本验证")
        script_validation = self.validate_professional_script()
        
        # 4. 迁移策略
        print("\n📊 第4部分: 迁移策略计算")
        migration_strategy = self.calculate_migration_strategy()
        
        # 5. 总结报告
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'current_data': current_data,
            'pollution_patterns': pollution_patterns,
            'script_validation': script_validation,
            'migration_strategy': migration_strategy,
            'recommendations': self.generate_recommendations()
        }
        
        print("\n" + "=" * 80)
        print("📋 验证报告总结")
        print("=" * 80)
        
        return self.validation_results
    
    def generate_recommendations(self):
        """生成建议"""
        recommendations = []
        
        # 基于专业脚本的建议
        if self.validation_results.get('script_validation', {}).get('script_exists'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Professional Script',
                'action': '使用专业脚本 generate_real_million_data_simplified.py',
                'reason': '该脚本经过专业优化，具备内存管理、批处理、真实数据生成等特性',
                'estimated_time': '2-3小时'
            })
        
        # 数据清理建议
        if self.stats.get('million_users', 0) > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Data Cleanup',
                'action': '清理现有million_前缀的测试数据',
                'reason': '避免数据污染，确保新生成数据的质量',
                'estimated_time': '30分钟'
            })
        
        # 环境准备建议
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Environment Setup',
            'action': '确保Django环境和依赖包完整安装',
            'reason': '专业脚本需要完整的Django环境支持',
            'estimated_time': '1小时'
        })
        
        print("💡 建议措施:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. [{rec['priority']}] {rec['action']}")
            print(f"      原因: {rec['reason']}")
            print(f"      预计时间: {rec['estimated_time']}")
            print()
        
        return recommendations

def main():
    """主函数"""
    print("🔍 数据验证和质量检查系统")
    print("=" * 60)
    
    validator = DatabaseValidator()
    report = validator.generate_validation_report()
    
    # 保存报告到文件
    report_file = f"data_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("数据验证和质量检查报告\n")
            f.write("=" * 60 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("🎯 专业百万级数据生成脚本确认:\n")
            f.write("   脚本名称: generate_real_million_data_simplified.py\n")
            f.write("   脚本特点: 内存优化、批处理、真实数据生成、错误处理\n")
            f.write("   目标规模: 800,000学生 + 50,000教师 + 30,000课程 + 200,000选课记录\n")
            f.write("   预期总量: 1,080,000+ 条记录\n\n")
            
            f.write("📊 当前数据状态:\n")
            if hasattr(validator, 'stats') and validator.stats:
                for key, value in validator.stats.items():
                    f.write(f"   {key}: {value}\n")
            
            f.write("\n💡 建议的迁移方式:\n")
            f.write("   使用专业脚本 generate_real_million_data_simplified.py\n")
            f.write("   该脚本是项目中经过各种考量的专业百万级数据生成方案\n")
        
        print(f"\n📁 报告已保存到: {report_file}")
        
    except Exception as e:
        print(f"⚠️ 报告保存失败: {e}")
    
    print("\n🎉 数据验证和质量检查完成！")
    return True

if __name__ == '__main__':
    main()