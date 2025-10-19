"""
算法性能对比工具
用于比较不同排课算法的性能
"""

import time
import json
from typing import Dict, List, Any
from datetime import datetime

from .algorithms import create_auto_schedule
from .genetic_algorithm import create_genetic_schedule
from .hybrid_algorithm import create_hybrid_schedule
from apps.courses.models import Course

class AlgorithmPerformanceComparator:
    """算法性能对比器"""
    
    def __init__(self, semester: str, academic_year: str):
        self.semester = semester
        self.academic_year = academic_year
        self.results = []
        
    def compare_algorithms(self, course_ids: List[int] = None, timeout_seconds: int = 300) -> Dict[str, Any]:
        """
        比较不同算法的性能
        
        Args:
            course_ids: 要排课的课程ID列表
            timeout_seconds: 算法执行超时时间
            
        Returns:
            性能对比结果
        """
        algorithms = [
            ('贪心算法', 'greedy', create_auto_schedule),
            ('遗传算法', 'genetic', create_genetic_schedule),
            ('混合算法', 'hybrid', create_hybrid_schedule)
        ]
        
        comparison_results = {
            'algorithms': [],
            'comparison': {},
            'timestamp': datetime.now().isoformat(),
            'semester': self.semester,
            'academic_year': self.academic_year
        }
        
        # 获取课程总数用于统计
        courses_query = Course.objects.filter(
            semester=self.semester,
            academic_year=self.academic_year,
            is_active=True,
            is_published=True
        )
        if course_ids:
            courses_query = courses_query.filter(id__in=course_ids)
        
        total_courses = courses_query.count()
        
        # 分别运行每个算法
        for algorithm_name, algorithm_type, algorithm_func in algorithms:
            print(f"🔄 正在运行{algorithm_name}...")
            
            try:
                start_time = time.time()
                
                # 运行算法
                if algorithm_type == 'greedy':
                    result = algorithm_func(self.semester, self.academic_year, course_ids, algorithm_type, timeout_seconds)
                else:
                    result = algorithm_func(self.semester, self.academic_year, course_ids)
                
                execution_time = time.time() - start_time
                
                # 提取关键指标
                success_rate = result.get('success_rate', 0)
                successful_assignments = result.get('successful_assignments', 0)
                total_constraints = result.get('total_constraints', 0)
                failed_assignments = len(result.get('failed_assignments', []))
                
                # 计算资源利用率指标
                resource_utilization = result.get('resource_utilization', {})
                classroom_usage = resource_utilization.get('classroom_usage', {})
                teacher_workload = resource_utilization.get('teacher_workload', {})
                
                # 计算教室利用率平衡度
                classroom_balance = self._calculate_balance_score(list(classroom_usage.values())) if classroom_usage else 0
                
                # 计算教师工作量平衡度
                teacher_balance = self._calculate_balance_score(list(teacher_workload.values())) if teacher_workload else 0
                
                algorithm_result = {
                    'name': algorithm_name,
                    'type': algorithm_type,
                    'execution_time': execution_time,
                    'success_rate': success_rate,
                    'successful_assignments': successful_assignments,
                    'total_constraints': total_constraints,
                    'failed_assignments': failed_assignments,
                    'classroom_balance': classroom_balance,
                    'teacher_balance': teacher_balance,
                    'total_courses': total_courses,
                    'status': 'completed'
                }
                
                comparison_results['algorithms'].append(algorithm_result)
                print(f"  ✅ {algorithm_name}完成: 成功率{success_rate:.1f}%, 耗时{execution_time:.2f}秒")
                
            except Exception as e:
                print(f"  ❌ {algorithm_name}失败: {str(e)}")
                algorithm_result = {
                    'name': algorithm_name,
                    'type': algorithm_type,
                    'execution_time': 0,
                    'success_rate': 0,
                    'successful_assignments': 0,
                    'total_constraints': 0,
                    'failed_assignments': 0,
                    'classroom_balance': 0,
                    'teacher_balance': 0,
                    'total_courses': total_courses,
                    'status': 'failed',
                    'error': str(e)
                }
                comparison_results['algorithms'].append(algorithm_result)
        
        # 生成对比分析
        comparison_results['comparison'] = self._generate_comparison_analysis(comparison_results['algorithms'])
        
        return comparison_results
    
    def _calculate_balance_score(self, values: List[float]) -> float:
        """
        计算平衡度分数
        
        Args:
            values: 数值列表
            
        Returns:
            平衡度分数 (0-1, 1表示完全平衡)
        """
        if not values:
            return 0
            
        if len(values) == 1:
            return 1
            
        # 计算方差
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        # 转换为平衡度分数 (方差越小，平衡度越高)
        if mean == 0:
            return 1 if variance == 0 else 0
            
        # 使用变异系数的倒数来计算平衡度
        coefficient_of_variation = (variance ** 0.5) / mean
        balance_score = max(0, 1 - min(1, coefficient_of_variation))
        
        return balance_score
    
    def _generate_comparison_analysis(self, algorithm_results: List[Dict]) -> Dict[str, Any]:
        """
        生成对比分析
        
        Args:
            algorithm_results: 算法结果列表
            
        Returns:
            对比分析结果
        """
        if not algorithm_results:
            return {}
        
        # 找到最佳算法
        completed_algorithms = [r for r in algorithm_results if r['status'] == 'completed']
        
        if not completed_algorithms:
            return {'best_algorithm': None, 'analysis': '所有算法都执行失败'}
        
        # 按成功率排序
        best_by_success = max(completed_algorithms, key=lambda x: x['success_rate'])
        
        # 按执行时间排序
        best_by_time = min(completed_algorithms, key=lambda x: x['execution_time'])
        
        # 按综合评分排序 (成功率70% + 执行时间30%)
        def composite_score(result):
            time_score = 1 - min(1, result['execution_time'] / 300)  # 假设300秒为最大可接受时间
            return result['success_rate'] * 0.7 + time_score * 30  # 时间权重转换为0-30分
        
        best_overall = max(completed_algorithms, key=composite_score)
        
        return {
            'best_by_success_rate': {
                'algorithm': best_by_success['name'],
                'success_rate': best_by_success['success_rate'],
                'reason': f'{best_by_success["name"]}达到了最高的成功率'
            },
            'best_by_execution_time': {
                'algorithm': best_by_time['name'],
                'execution_time': best_by_time['execution_time'],
                'reason': f'{best_by_time["name"]}执行速度最快'
            },
            'best_overall': {
                'algorithm': best_overall['name'],
                'success_rate': best_overall['success_rate'],
                'execution_time': best_overall['execution_time'],
                'reason': f'{best_overall["name"]}在成功率和执行时间之间达到了最佳平衡'
            }
        }
    
    def generate_detailed_report(self, comparison_results: Dict[str, Any]) -> str:
        """
        生成详细对比报告
        
        Args:
            comparison_results: 对比结果
            
        Returns:
            详细报告文本
        """
        report = []
        report.append("=" * 80)
        report.append("智能排课算法性能对比报告")
        report.append("=" * 80)
        report.append(f"生成时间: {comparison_results['timestamp']}")
        report.append(f"学期: {comparison_results['semester']}")
        report.append(f"学年: {comparison_results['academic_year']}")
        report.append("")
        
        # 算法详细结果
        report.append("算法详细结果:")
        report.append("-" * 80)
        report.append(f"{'算法名称':<12} {'状态':<8} {'成功率':<8} {'成功数':<8} {'失败数':<8} {'耗时(秒)':<10} {'教室平衡':<8} {'教师平衡':<8}")
        report.append("-" * 80)
        
        for result in comparison_results['algorithms']:
            if result['status'] == 'completed':
                report.append(f"{result['name']:<12} {result['status']:<8} {result['success_rate']:<8.1f} "
                            f"{result['successful_assignments']:<8} {result['failed_assignments']:<8} "
                            f"{result['execution_time']:<10.2f} {result['classroom_balance']:<8.2f} "
                            f"{result['teacher_balance']:<8.2f}")
            else:
                report.append(f"{result['name']:<12} {result['status']:<8} {'失败':<8} {'-':<8} {'-':<8} {'-':<10} {'-':<8} {'-':<8}")
        
        report.append("")
        
        # 对比分析
        comparison = comparison_results['comparison']
        if comparison:
            report.append("对比分析:")
            report.append("-" * 40)
            if 'best_by_success_rate' in comparison:
                best_success = comparison['best_by_success_rate']
                report.append(f"最高成功率: {best_success['algorithm']} ({best_success['success_rate']:.1f}%)")
                report.append(f"  原因: {best_success['reason']}")
            
            if 'best_by_execution_time' in comparison:
                best_time = comparison['best_by_execution_time']
                report.append(f"最快执行: {best_time['algorithm']} ({best_time['execution_time']:.2f}秒)")
                report.append(f"  原因: {best_time['reason']}")
            
            if 'best_overall' in comparison:
                best_overall = comparison['best_overall']
                report.append(f"综合最佳: {best_overall['algorithm']}")
                report.append(f"  成功率: {best_overall['success_rate']:.1f}%")
                report.append(f"  执行时间: {best_overall['execution_time']:.2f}秒")
                report.append(f"  原因: {best_overall['reason']}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def run_performance_comparison(semester: str, academic_year: str, course_ids: List[int] = None, 
                             timeout_seconds: int = 300) -> Dict[str, Any]:
    """
    运行算法性能对比
    
    Args:
        semester: 学期
        academic_year: 学年
        course_ids: 课程ID列表
        timeout_seconds: 超时时间
        
    Returns:
        对比结果
    """
    comparator = AlgorithmPerformanceComparator(semester, academic_year)
    results = comparator.compare_algorithms(course_ids, timeout_seconds)
    
    # 生成并打印详细报告
    report = comparator.generate_detailed_report(results)
    print(report)
    
    return results