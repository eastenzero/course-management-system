# file: data-generator/optimized_main.py
# 功能: 优化后的数据生成主脚本

import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from config import DATA_SCALE_CONFIG
from generators import (
    DepartmentGenerator,
    UserGenerator,
    CourseGenerator,
    FacilityGenerator,
    DataExporter
)
from generators.realistic_constraints import RealisticConstraintsEngine
from generators.relationship_modeling import RelationshipModelingEngine
from generators.conflict_generator import ConflictGeneratorEngine
from generators.quality_assessment import DataQualityAssessment


class OptimizedDataGenerator:
    """优化后的数据生成器
    
    集成真实性约束、关联性建模、冲突生成和质量评估功能
    """
    
    def __init__(self):
        self.realistic_engine = RealisticConstraintsEngine()
        self.relationship_engine = RelationshipModelingEngine()
        self.conflict_engine = ConflictGeneratorEngine()
        self.quality_assessor = DataQualityAssessment()
        
    def generate_enhanced_dataset(self, scale: str = 'medium', 
                                output_dir: str = 'output',
                                conflict_difficulty: str = 'mixed') -> Dict[str, Any]:
        """生成增强的数据集
        
        Args:
            scale: 数据规模
            output_dir: 输出目录
            conflict_difficulty: 冲突难度级别
            
        Returns:
            增强的数据集
        """
        print(f"🚀 开始生成优化的{scale}规模数据集...")
        config = DATA_SCALE_CONFIG[scale]
        start_time = time.time()
        
        # 1. 生成基础数据
        print("📚 生成基础数据...")
        basic_dataset = self._generate_basic_data(config)
        
        # 2. 应用真实性约束
        print("🎯 应用真实性约束...")
        enhanced_dataset = self._apply_realistic_constraints(basic_dataset)
        
        # 3. 构建关联性模型
        print("🔗 构建关联性模型...")
        modeled_dataset = self._build_relationship_model(enhanced_dataset)
        
        # 4. 生成冲突场景
        print("⚡ 生成冲突场景...")
        conflict_dataset = self._generate_conflicts(modeled_dataset, conflict_difficulty)
        
        # 5. 质量评估
        print("📊 进行质量评估...")
        quality_report = self.quality_assessor.generate_quality_report(conflict_dataset)
        conflict_dataset['quality_report'] = quality_report
        
        generation_time = time.time() - start_time
        
        print(f"✅ 数据生成完成！耗时: {generation_time:.2f}秒")
        print(f"📈 质量分数: {quality_report['assessment_summary']['overall_score']:.3f}")
        print(f"🏆 质量等级: {quality_report['assessment_summary']['grade']}")
        
        return conflict_dataset
    
    def _generate_basic_data(self, config: Dict) -> Dict[str, Any]:
        """生成基础数据"""
        # 初始化生成器
        dept_gen = DepartmentGenerator()
        user_gen = UserGenerator()
        course_gen = CourseGenerator()
        facility_gen = FacilityGenerator()
        
        # 生成基础数据
        departments = dept_gen.generate_departments(config['departments'])
        majors = dept_gen.generate_majors(departments)
        students = user_gen.generate_students(config['students'], majors)
        teachers = user_gen.generate_teachers(config['teachers'], departments)
        courses = course_gen.generate_courses(config['courses'], departments, teachers)
        classrooms = facility_gen.generate_classrooms(config['classrooms'])
        time_slots = facility_gen.generate_time_slots()
        
        return {
            'departments': departments,
            'majors': majors,
            'students': students,
            'teachers': teachers,
            'courses': courses,
            'classrooms': classrooms,
            'time_slots': time_slots,
            'metadata': {
                'scale': config,
                'generation_stage': 'basic'
            }
        }
    
    def _apply_realistic_constraints(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """应用真实性约束"""
        enhanced_dataset = dataset.copy()
        
        # 生成真实的教师时间偏好
        teacher_preferences = []
        for teacher in dataset['teachers']:
            prefs = self.realistic_engine.generate_realistic_teacher_preferences(teacher)
            teacher_preferences.append(prefs)
        enhanced_dataset['teacher_preferences'] = teacher_preferences
        
        # 增强课程真实性
        enhanced_courses = self.realistic_engine.generate_realistic_course_distribution(
            dataset['courses'], dataset['departments']
        )
        enhanced_dataset['courses'] = enhanced_courses
        
        # 生成真实的选课模式
        realistic_enrollments = self.realistic_engine.generate_realistic_student_enrollment_patterns(
            dataset['students'], enhanced_courses
        )
        enhanced_dataset['enrollments'] = realistic_enrollments
        
        enhanced_dataset['metadata']['generation_stage'] = 'realistic_enhanced'
        return enhanced_dataset
    
    def _build_relationship_model(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """构建关联性模型"""
        modeled_dataset = dataset.copy()
        
        # 构建课程依赖网络
        course_dependencies = self.relationship_engine.build_course_dependency_network(
            dataset['courses']
        )
        modeled_dataset['course_dependencies'] = course_dependencies
        
        # 生成教师能力档案
        teacher_competencies = self.relationship_engine.generate_teacher_competency_profiles(
            dataset['teachers'], dataset['departments']
        )
        modeled_dataset['teacher_competencies'] = teacher_competencies
        
        # 优化教师课程分配
        optimized_assignments = self.relationship_engine.optimize_teacher_course_assignments(
            dataset['courses'], dataset['teachers']
        )
        modeled_dataset['optimized_assignments'] = optimized_assignments
        
        modeled_dataset['metadata']['generation_stage'] = 'relationship_modeled'
        return modeled_dataset
    
    def _generate_conflicts(self, dataset: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
        """生成冲突场景"""
        conflict_dataset = dataset.copy()
        
        # 生成冲突场景
        conflict_scenarios = self.conflict_engine.generate_conflict_scenarios(
            dataset['courses'], 
            dataset['teachers'], 
            dataset['classrooms'],
            target_difficulty=difficulty
        )
        conflict_dataset['conflicts'] = conflict_scenarios
        
        # 生成冲突统计
        conflict_stats = self.conflict_engine.generate_conflict_statistics()
        conflict_dataset['conflict_statistics'] = conflict_stats
        
        conflict_dataset['metadata']['generation_stage'] = 'conflict_enhanced'
        conflict_dataset['metadata']['conflict_difficulty'] = difficulty
        
        return conflict_dataset


def main():
    """主函数"""
    generator = OptimizedDataGenerator()
    
    # 生成不同规模的数据集进行对比
    scales = ['small', 'medium']  # 限制规模以节省时间
    
    for scale in scales:
        print(f"\n{'='*60}")
        print(f"生成{scale}规模优化数据集")
        print(f"{'='*60}")
        
        try:
            dataset = generator.generate_enhanced_dataset(
                scale=scale,
                conflict_difficulty='mixed'
            )
            
            # 保存数据集
            exporter = DataExporter('output')
            exporter.export_to_json(dataset, f'optimized_{scale}_dataset.json')
            
            # 导出冲突场景
            generator.conflict_engine.export_conflict_scenarios(f'output/conflicts_{scale}.json')
            
            print(f"\n📋 {scale}规模数据集统计:")
            print(f"   - 学生: {len(dataset.get('students', []))} 人")
            print(f"   - 教师: {len(dataset.get('teachers', []))} 人") 
            print(f"   - 课程: {len(dataset.get('courses', []))} 门")
            print(f"   - 选课记录: {len(dataset.get('enrollments', []))} 条")
            print(f"   - 冲突场景: {len(dataset.get('conflicts', []))} 个")
            
            quality_report = dataset.get('quality_report', {})
            if quality_report:
                print(f"\n📊 质量评估结果:")
                scores = quality_report.get('detailed_scores', {})
                for metric, score in scores.items():
                    print(f"   - {metric}: {score:.3f}")
            
        except Exception as e:
            print(f"❌ 生成{scale}规模数据集时出错: {e}")
            continue


if __name__ == "__main__":
    main()