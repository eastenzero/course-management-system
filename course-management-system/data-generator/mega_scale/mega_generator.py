# file: data-generator/mega_scale/mega_generator.py
# 功能: 百万级数据生成主控制器

import sys
import time
import json
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

# 添加上级目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from .batch_manager import BatchProcessingManager, BatchConfig
from .memory_optimizer import MemoryOptimizer, StreamConfig
from .parallel_engine import ParallelComputingEngine, TaskConfig, TaskResult
from .progress_monitor import ProgressMonitor

# 导入原有的生成器
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


@dataclass
class MegaGenerationConfig:
    """百万级生成配置"""
    target_records: int = 1000000     # 目标记录数
    batch_size: int = 50000           # 批次大小
    max_memory_mb: int = 2048         # 最大内存限制
    max_workers: int = 8              # 最大工作进程数
    enable_compression: bool = True    # 启用压缩
    enable_streaming: bool = True      # 启用流式写入
    enable_checkpoints: bool = True    # 启用检查点
    output_formats: List[str] = None   # 输出格式
    
    def __post_init__(self):
        if self.output_formats is None:
            self.output_formats = ['json']


class MegaDataGenerator:
    """百万级数据生成器"""
    
    def __init__(self, config: MegaGenerationConfig = None):
        self.config = config or MegaGenerationConfig()
        
        # 初始化核心组件
        self.batch_manager = BatchProcessingManager(BatchConfig(
            batch_size=self.config.batch_size,
            max_memory_mb=self.config.max_memory_mb,
            max_workers=self.config.max_workers,
            enable_compression=self.config.enable_compression,
            enable_streaming=self.config.enable_streaming
        ))
        
        self.memory_optimizer = MemoryOptimizer(self.config.max_memory_mb)
        
        self.parallel_engine = ParallelComputingEngine(self.config.max_workers)
        
        self.progress_monitor = ProgressMonitor(self.config.target_records)
        
        # 原有生成器组件
        self.realistic_engine = RealisticConstraintsEngine()
        self.relationship_engine = RelationshipModelingEngine()
        self.conflict_engine = ConflictGeneratorEngine()
        self.quality_assessor = DataQualityAssessment()
        
        # 状态跟踪
        self.generation_started = False
        self.generation_completed = False
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # 结果存储
        self.final_results: Dict[str, Any] = {}
        self.performance_stats: Dict[str, Any] = {}
    
    def generate_mega_dataset(self, scale: str = 'huge', 
                            output_dir: str = 'mega_output',
                            conflict_difficulty: str = 'mixed') -> Dict[str, Any]:
        """生成百万级数据集"""
        
        print(f"\n{'='*80}")
        print(f"🚀 开始百万级数据生成系统")
        print(f"📊 目标规模: {self.config.target_records:,} 条记录")
        print(f"🔧 批次大小: {self.config.batch_size:,}")
        print(f"💾 内存限制: {self.config.max_memory_mb}MB")
        print(f"⚡ 并行度: {self.config.max_workers} 工作进程")
        print(f"{'='*80}")
        
        self.generation_started = True
        self.start_time = time.time()
        
        try:
            # 1. 系统初始化和优化
            self._initialize_system()
            
            # 2. 启动监控
            self.progress_monitor.start_monitoring(enable_progress_bar=True)
            
            # 3. 生成基础数据
            print("\n📚 阶段1: 生成基础数据...")
            basic_dataset = self._generate_basic_data_mega(scale)
            
            # 4. 应用真实性约束
            print("\n🎯 阶段2: 应用真实性约束...")
            enhanced_dataset = self._apply_realistic_constraints_mega(basic_dataset)
            
            # 5. 构建关联性模型
            print("\n🔗 阶段3: 构建关联性模型...")
            modeled_dataset = self._build_relationship_model_mega(enhanced_dataset)
            
            # 6. 生成冲突场景
            print("\n⚡ 阶段4: 生成冲突场景...")
            conflict_dataset = self._generate_conflicts_mega(modeled_dataset, conflict_difficulty)
            
            # 7. 质量评估
            print("\n📊 阶段5: 质量评估...")
            quality_report = self._assess_quality_mega(conflict_dataset)
            conflict_dataset['quality_report'] = quality_report
            
            # 8. 数据导出
            print("\n💾 阶段6: 数据导出...")
            self._export_data_mega(conflict_dataset, output_dir)
            
            # 9. 最终统计
            self._finalize_generation(conflict_dataset)
            
            return self.final_results
            
        except Exception as e:
            error_id = self.progress_monitor.handle_error(e, {
                'stage': 'mega_generation',
                'config': self.config.__dict__
            })
            print(f"❌ 生成过程发生错误: {e}")
            print(f"🔍 错误ID: {error_id}")
            raise
        
        finally:
            self._cleanup_resources()
    
    def _initialize_system(self):
        """初始化系统"""
        print("⚙️ 初始化百万级数据生成系统...")
        
        # 初始化并行引擎
        self.parallel_engine.initialize_workers(
            process_workers=max(1, self.config.max_workers // 2),
            thread_workers=max(1, self.config.max_workers // 2)
        )
        
        # 启动并行引擎
        self.parallel_engine.start_processing()
        
        # 内存优化设置
        optimization_result = self.memory_optimizer.optimize_for_large_scale(
            self.config.target_records
        )
        
        print(f"   ✅ 并行引擎: {self.config.max_workers} 工作进程")
        print(f"   ✅ 内存优化: {len(optimization_result['optimizations_applied'])} 项优化")
        print(f"   ✅ 批次配置: {self.config.batch_size:,} 记录/批次")
        
        # 注册任务处理函数
        self._register_task_functions()
    
    def _register_task_functions(self):
        """注册任务处理函数"""
        self.parallel_engine.register_task_function('generate_students', self._generate_students_batch)
        self.parallel_engine.register_task_function('generate_teachers', self._generate_teachers_batch)
        self.parallel_engine.register_task_function('generate_courses', self._generate_courses_batch)
        self.parallel_engine.register_task_function('apply_constraints', self._apply_constraints_batch)
        self.parallel_engine.register_task_function('build_relationships', self._build_relationships_batch)
        self.parallel_engine.register_task_function('generate_conflicts', self._generate_conflicts_batch)
    
    def _generate_basic_data_mega(self, scale: str) -> Dict[str, Any]:
        """大规模生成基础数据"""
        config = DATA_SCALE_CONFIG[scale]
        
        # 使用批处理管理器创建批次
        total_student_records = config['students']
        student_batches = self.batch_manager.create_batches(total_student_records)
        
        print(f"   📊 规划 {len(student_batches)} 个学生批次")
        
        # 生成院系、专业等基础数据（这些数据量较小，直接生成）
        print("   🏢 生成院系和专业...")
        dept_gen = DepartmentGenerator()
        departments = dept_gen.generate_departments(config['departments'])
        majors = dept_gen.generate_majors(departments)
        
        print("   🏫 生成教室和时间段...")
        facility_gen = FacilityGenerator()
        classrooms = facility_gen.generate_classrooms(config['classrooms'])
        time_slots = facility_gen.generate_time_slots()
        
        # 并行生成大量数据
        print("   👥 并行生成学生数据...")
        students = self._generate_students_parallel(config['students'], majors)
        
        print("   👨‍🏫 并行生成教师数据...")
        teachers = self._generate_teachers_parallel(config['teachers'], departments)
        
        print("   📚 并行生成课程数据...")
        courses = self._generate_courses_parallel(config['courses'], departments, teachers)
        
        # 更新进度
        total_generated = len(students) + len(teachers) + len(courses)
        self.progress_monitor.update_progress(total_generated)
        
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
                'generation_stage': 'basic_mega',
                'total_records': total_generated
            }
        }
    
    def _generate_students_parallel(self, total_students: int, majors: List[Dict]) -> List[Dict]:
        """并行生成学生数据"""
        # 创建批次任务
        batch_size = self.config.batch_size
        num_batches = (total_students + batch_size - 1) // batch_size
        
        task_configs = []
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_students)
            
            task_config = TaskConfig(
                task_id=f"student_batch_{i}",
                task_type="generate_students",
                priority=5,
                estimated_duration=30.0,
                memory_requirement_mb=100
            )
            task_configs.append((task_config, self._generate_students_batch, (start_idx, end_idx, majors), {}))
        
        # 提交任务
        task_ids = self.parallel_engine.submit_batch_tasks(task_configs)
        
        # 等待完成并合并结果
        self.parallel_engine.wait_for_completion()
        results = self.parallel_engine.get_results()
        
        # 合并学生数据
        all_students = []
        for task_id in task_ids:
            if task_id in results and results[task_id].success:
                batch_students = results[task_id].result
                all_students.extend(batch_students)
        
        return all_students
    
    def _generate_teachers_parallel(self, total_teachers: int, departments: List[Dict]) -> List[Dict]:
        """并行生成教师数据"""
        # 教师数量相对较少，可以用较小的批次
        batch_size = min(5000, self.config.batch_size // 10)
        num_batches = (total_teachers + batch_size - 1) // batch_size
        
        task_configs = []
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_teachers)
            
            task_config = TaskConfig(
                task_id=f"teacher_batch_{i}",
                task_type="generate_teachers",
                priority=5,
                estimated_duration=15.0,
                memory_requirement_mb=50
            )
            task_configs.append((task_config, self._generate_teachers_batch, (start_idx, end_idx, departments), {}))
        
        # 提交并执行任务
        task_ids = self.parallel_engine.submit_batch_tasks(task_configs)
        self.parallel_engine.wait_for_completion()
        results = self.parallel_engine.get_results()
        
        # 合并教师数据
        all_teachers = []
        for task_id in task_ids:
            if task_id in results and results[task_id].success:
                batch_teachers = results[task_id].result
                all_teachers.extend(batch_teachers)
        
        return all_teachers
    
    def _generate_courses_parallel(self, total_courses: int, departments: List[Dict], teachers: List[Dict]) -> List[Dict]:
        """并行生成课程数据"""
        batch_size = min(10000, self.config.batch_size // 5)
        num_batches = (total_courses + batch_size - 1) // batch_size
        
        task_configs = []
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_courses)
            
            task_config = TaskConfig(
                task_id=f"course_batch_{i}",
                task_type="generate_courses",
                priority=5,
                estimated_duration=20.0,
                memory_requirement_mb=75
            )
            task_configs.append((task_config, self._generate_courses_batch, (start_idx, end_idx, departments, teachers), {}))
        
        # 提交并执行任务
        task_ids = self.parallel_engine.submit_batch_tasks(task_configs)
        self.parallel_engine.wait_for_completion()
        results = self.parallel_engine.get_results()
        
        # 合并课程数据
        all_courses = []
        for task_id in task_ids:
            if task_id in results and results[task_id].success:
                batch_courses = results[task_id].result
                all_courses.extend(batch_courses)
        
        return all_courses
    
    def _generate_students_batch(self, start_idx: int, end_idx: int, majors: List[Dict]) -> List[Dict]:
        """生成一批学生数据"""
        user_gen = UserGenerator()
        batch_size = end_idx - start_idx
        
        students = []
        for i in range(batch_size):
            student_id = start_idx + i + 1
            student = user_gen.generate_student(student_id, majors)
            students.append(student)
        
        return students
    
    def _generate_teachers_batch(self, start_idx: int, end_idx: int, departments: List[Dict]) -> List[Dict]:
        """生成一批教师数据"""
        user_gen = UserGenerator()
        batch_size = end_idx - start_idx
        
        teachers = []
        for i in range(batch_size):
            teacher_id = start_idx + i + 1
            teacher = user_gen.generate_teacher(teacher_id, departments)
            teachers.append(teacher)
        
        return teachers
    
    def _generate_courses_batch(self, start_idx: int, end_idx: int, 
                               departments: List[Dict], teachers: List[Dict]) -> List[Dict]:
        """生成一批课程数据"""
        course_gen = CourseGenerator()
        batch_size = end_idx - start_idx
        
        courses = []
        for i in range(batch_size):
            course = course_gen.generate_course(departments, teachers)
            courses.append(course)
        
        return courses
    
    def _apply_constraints_batch(self, *args, **kwargs) -> List[Dict]:
        """应用约束条件批处理"""
        # 这是一个占位符方法，用于约束处理
        # 在实际实现中，这里会处理各种约束条件
        return []
    
    def _build_relationships_batch(self, *args, **kwargs) -> List[Dict]:
        """构建关系批处理"""
        # 这是一个占位符方法，用于关系构建
        return []
    
    def _generate_conflicts_batch(self, *args, **kwargs) -> List[Dict]:
        """生成冲突批处理"""
        # 这是一个占位符方法，用于冲突生成
        return []
    
    def _apply_realistic_constraints_mega(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """大规模应用真实性约束"""
        print("   ⚙️ 应用真实性约束...")
        
        enhanced_dataset = dataset.copy()
        
        # 分批处理教师偏好
        print("   📋 生成教师偏好...")
        teacher_preferences = []
        batch_size = 5000
        
        for i in range(0, len(dataset['teachers']), batch_size):
            batch_teachers = dataset['teachers'][i:i+batch_size]
            
            for teacher in batch_teachers:
                prefs = self.realistic_engine.generate_realistic_teacher_preferences(teacher)
                teacher_preferences.append(prefs)
            
            # 增量写入
            if self.config.enable_streaming:
                self.memory_optimizer.write_incrementally(
                    'mega_output/teacher_preferences_batch.json',
                    teacher_preferences[-len(batch_teachers):],
                    'json'
                )
            
            # 更新进度
            self.progress_monitor.update_progress(
                self.progress_monitor.current_metrics.processed_records + len(batch_teachers)
            )
        
        enhanced_dataset['teacher_preferences'] = teacher_preferences
        
        # 增强课程真实性
        print("   📚 增强课程真实性...")
        enhanced_courses = self.realistic_engine.generate_realistic_course_distribution(
            dataset['courses'], dataset['departments']
        )
        enhanced_dataset['courses'] = enhanced_courses
        
        # 生成选课模式
        print("   🎓 生成选课模式...")
        enrollments = self.realistic_engine.generate_realistic_student_enrollment_patterns(
            dataset['students'], enhanced_courses
        )
        enhanced_dataset['enrollments'] = enrollments
        
        enhanced_dataset['metadata']['generation_stage'] = 'realistic_enhanced_mega'
        return enhanced_dataset
    
    def _build_relationship_model_mega(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """大规模构建关联性模型"""
        print("   🔗 构建关联性模型...")
        
        modeled_dataset = dataset.copy()
        
        # 生成课程依赖关系
        print("   📖 生成课程依赖关系...")
        dependencies = self.relationship_engine.generate_course_dependencies(dataset['courses'])
        modeled_dataset['course_dependencies'] = dependencies
        
        # 分批生成教师能力档案
        print("   👨‍🏫 生成教师能力档案...")
        teacher_competencies = []
        batch_size = 1000
        
        for i in range(0, len(dataset['teachers']), batch_size):
            batch_teachers = dataset['teachers'][i:i+batch_size]
            batch_competencies = self.relationship_engine.generate_teacher_competency_profiles(
                batch_teachers, dataset['departments']
            )
            teacher_competencies.extend(batch_competencies)
            
            # 定期触发内存优化
            self.memory_optimizer.trigger_gc_if_needed()
        
        modeled_dataset['teacher_competencies'] = teacher_competencies
        
        # 优化教师课程分配
        print("   🎯 优化教师课程分配...")
        optimized_assignments = self.relationship_engine.optimize_teacher_course_assignments(
            dataset['courses'], dataset['teachers']
        )
        modeled_dataset['optimized_assignments'] = optimized_assignments
        
        modeled_dataset['metadata']['generation_stage'] = 'relationship_modeled_mega'
        return modeled_dataset
    
    def _generate_conflicts_mega(self, dataset: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
        """大规模生成冲突场景"""
        print("   ⚡ 生成冲突场景...")
        
        conflict_dataset = dataset.copy()
        
        # 生成冲突场景
        print(f"   ⚙️ 生成{difficulty}级别冲突场景...")
        conflict_scenarios = self.conflict_engine.generate_conflict_scenarios(
            dataset['courses'], 
            dataset['teachers'], 
            dataset['classrooms'],
            target_difficulty=difficulty
        )
        conflict_dataset['conflicts'] = conflict_scenarios
        
        # 生成冲突统计
        print("   📊 生成冲突统计...")
        conflict_stats = self.conflict_engine.generate_conflict_statistics()
        conflict_dataset['conflict_statistics'] = conflict_stats
        
        conflict_dataset['metadata']['generation_stage'] = 'conflict_enhanced_mega'
        conflict_dataset['metadata']['conflict_difficulty'] = difficulty
        
        return conflict_dataset
    
    def _assess_quality_mega(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """大规模质量评估"""
        print("   📊 进行质量评估...")
        
        # 采样评估以提高性能
        sample_size = min(10000, len(dataset.get('students', [])) // 100)
        
        print(f"   🔍 采样评估 (样本大小: {sample_size:,})")
        
        quality_report = self.quality_assessor.generate_quality_report(
            dataset, sample_size=sample_size
        )
        
        return quality_report
    
    def _export_data_mega(self, dataset: Dict[str, Any], output_dir: str):
        """大规模数据导出"""
        print(f"   💾 导出数据到 {output_dir}...")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 分别导出各类数据
        exporter = DataExporter(str(output_path))
        
        for data_type in ['students', 'teachers', 'courses', 'enrollments']:
            if data_type in dataset:
                data = dataset[data_type]
                
                print(f"   📁 导出 {data_type}: {len(data):,} 条记录")
                
                # 分文件导出大数据
                if len(data) > 100000:
                    self._export_large_data(data, data_type, output_path)
                else:
                    exporter.export_to_json(data, f'{data_type}.json')
        
        # 导出元数据和报告
        exporter.export_to_json(dataset['metadata'], 'metadata.json')
        if 'quality_report' in dataset:
            exporter.export_to_json(dataset['quality_report'], 'quality_report.json')
    
    def _export_large_data(self, data: List[Dict], data_type: str, output_path: Path):
        """导出大型数据集"""
        chunk_size = 50000
        
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            chunk_file = output_path / f"{data_type}_part_{i//chunk_size + 1:03d}.json"
            
            if self.config.enable_compression:
                chunk_file = chunk_file.with_suffix('.json.gz')
            
            # 使用流式写入
            for record in chunk:
                self.memory_optimizer.write_incrementally(str(chunk_file), record, 'json')
    
    def _finalize_generation(self, dataset: Dict[str, Any]):
        """完成生成过程"""
        self.end_time = time.time()
        self.generation_completed = True
        
        # 收集性能统计
        self.performance_stats = {
            'total_time': self.end_time - self.start_time,
            'total_records': sum(len(dataset.get(key, [])) for key in ['students', 'teachers', 'courses']),
            'memory_stats': self.memory_optimizer.get_optimization_stats(),
            'parallel_stats': self.parallel_engine.get_performance_stats(),
            'progress_report': self.progress_monitor.get_status_report()
        }
        
        # 存储最终结果
        self.final_results = {
            'dataset': dataset,
            'performance_stats': self.performance_stats,
            'config': self.config.__dict__,
            'success': True
        }
        
        # 打印最终报告
        self._print_final_report()
    
    def _print_final_report(self):
        """打印最终报告"""
        stats = self.performance_stats
        
        print(f"\n{'='*80}")
        print(f"🎉 百万级数据生成完成！")
        print(f"{'='*80}")
        print(f"⏱️  总耗时: {stats['total_time']:.1f} 秒")
        print(f"📊 总记录数: {stats['total_records']:,}")
        print(f"🚀 平均速度: {stats['total_records']/stats['total_time']:.0f} 条/秒")
        print(f"💾 峰值内存: {stats['memory_stats']['peak_memory_mb']:.0f}MB")
        print(f"🧹 GC次数: {stats['memory_stats']['gc_count']}")
        print(f"⚡ 并行效率: {stats['parallel_stats']['parallel_efficiency']:.1f}%")
        
        errors = stats['progress_report']['errors']
        if errors['total_errors'] > 0:
            print(f"❌ 总错误数: {errors['total_errors']} (解决率: {errors['resolution_rate']:.1f}%)")
        
        print(f"{'='*80}")
    
    def _cleanup_resources(self):
        """清理资源"""
        print("🧹 清理系统资源...")
        
        # 停止监控
        self.progress_monitor.stop_monitoring()
        
        # 停止并行引擎
        self.parallel_engine.stop()
        
        # 清理内存优化器
        self.memory_optimizer.cleanup()
        
        print("✅ 资源清理完成")


def main():
    """主函数示例"""
    
    # 配置百万级生成参数
    config = MegaGenerationConfig(
        target_records=1000000,
        batch_size=50000,
        max_memory_mb=2048,
        max_workers=8,
        enable_compression=True,
        enable_streaming=True,
        output_formats=['json']
    )
    
    # 创建生成器
    generator = MegaDataGenerator(config)
    
    try:
        # 开始生成
        results = generator.generate_mega_dataset(
            scale='huge',
            output_dir='mega_output',
            conflict_difficulty='mixed'
        )
        
        print("🎊 百万级数据生成成功完成！")
        return results
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return None


if __name__ == "__main__":
    main()