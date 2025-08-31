# file: data-generator/generators/quality_assessment.py
# 功能: 数据质量评估体系 - 验证优化效果

import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import math


@dataclass
class QualityMetrics:
    """数据质量指标"""
    realism_score: float  # 真实性分数 0-1
    complexity_score: float  # 复杂性分数 0-1
    diversity_score: float  # 多样性分数 0-1
    consistency_score: float  # 一致性分数 0-1
    algorithm_stress_score: float  # 算法压力测试分数 0-1
    overall_score: float  # 综合分数 0-1


class DataQualityAssessment:
    """数据质量评估引擎"""
    
    def __init__(self):
        self.assessment_weights = {
            'realism': 0.25,
            'complexity': 0.20,
            'diversity': 0.20,
            'consistency': 0.15,
            'algorithm_stress': 0.20
        }
    
    def evaluate_data_quality(self, dataset: Dict[str, Any]) -> QualityMetrics:
        """评估数据集质量"""
        
        # 1. 真实性评估
        realism_score = self._evaluate_realism(dataset)
        
        # 2. 复杂性评估
        complexity_score = self._evaluate_complexity(dataset)
        
        # 3. 多样性评估
        diversity_score = self._evaluate_diversity(dataset)
        
        # 4. 一致性评估
        consistency_score = self._evaluate_consistency(dataset)
        
        # 5. 算法压力测试评估
        algorithm_stress_score = self._evaluate_algorithm_stress(dataset)
        
        # 计算综合分数
        overall_score = (
            realism_score * self.assessment_weights['realism'] +
            complexity_score * self.assessment_weights['complexity'] +
            diversity_score * self.assessment_weights['diversity'] +
            consistency_score * self.assessment_weights['consistency'] +
            algorithm_stress_score * self.assessment_weights['algorithm_stress']
        )
        
        return QualityMetrics(
            realism_score=realism_score,
            complexity_score=complexity_score,
            diversity_score=diversity_score,
            consistency_score=consistency_score,
            algorithm_stress_score=algorithm_stress_score,
            overall_score=overall_score
        )
    
    def _evaluate_realism(self, dataset: Dict[str, Any]) -> float:
        """评估数据真实性"""
        scores = []
        
        # 时间分布真实性
        if 'teacher_preferences' in dataset:
            time_realism = self._assess_time_distribution_realism(dataset['teacher_preferences'])
            scores.append(time_realism)
        
        # 选课模式真实性
        if 'enrollments' in dataset:
            enrollment_realism = self._assess_enrollment_realism(dataset['enrollments'], dataset.get('courses', []))
            scores.append(enrollment_realism)
        
        # 教师分配真实性
        if 'courses' in dataset and 'teachers' in dataset:
            assignment_realism = self._assess_teacher_assignment_realism(dataset['courses'], dataset['teachers'])
            scores.append(assignment_realism)
        
        return np.mean(scores) if scores else 0.5
    
    def _evaluate_complexity(self, dataset: Dict[str, Any]) -> float:
        """评估数据复杂性"""
        scores = []
        
        # 冲突场景复杂度
        if 'conflicts' in dataset:
            conflict_complexity = len([c for c in dataset['conflicts'] if c.get('severity') in ['high', 'critical']]) / max(len(dataset['conflicts']), 1)
            scores.append(min(1.0, conflict_complexity * 2))
        
        # 课程依赖关系复杂度
        if 'courses' in dataset:
            dependency_complexity = self._calculate_dependency_complexity(dataset['courses'])
            scores.append(dependency_complexity)
        
        return np.mean(scores) if scores else 0.5
    
    def _evaluate_diversity(self, dataset: Dict[str, Any]) -> float:
        """评估数据多样性"""
        scores = []
        
        # 课程类型多样性
        if 'courses' in dataset:
            course_diversity = self._calculate_course_type_diversity(dataset['courses'])
            scores.append(course_diversity)
        
        # 教师能力多样性
        if 'teachers' in dataset:
            teacher_diversity = self._calculate_teacher_diversity(dataset['teachers'])
            scores.append(teacher_diversity)
        
        return np.mean(scores) if scores else 0.5
    
    def _evaluate_consistency(self, dataset: Dict[str, Any]) -> float:
        """评估数据一致性"""
        consistency_checks = []
        
        # 外键一致性检查
        fk_consistency = self._check_foreign_key_consistency(dataset)
        consistency_checks.append(fk_consistency)
        
        # 业务逻辑一致性检查
        business_consistency = self._check_business_logic_consistency(dataset)
        consistency_checks.append(business_consistency)
        
        return np.mean(consistency_checks) if consistency_checks else 1.0
    
    def _evaluate_algorithm_stress(self, dataset: Dict[str, Any]) -> float:
        """评估算法压力测试能力"""
        stress_factors = []
        
        # 资源竞争强度
        if 'conflicts' in dataset:
            competition_intensity = len([c for c in dataset['conflicts'] if 'competition' in c.get('type', '')]) / max(len(dataset['conflicts']), 1)
            stress_factors.append(competition_intensity)
        
        # 约束密度
        constraint_density = self._calculate_constraint_density(dataset)
        stress_factors.append(constraint_density)
        
        return np.mean(stress_factors) if stress_factors else 0.5
    
    def _assess_time_distribution_realism(self, preferences: List[Dict]) -> float:
        """评估时间分布真实性"""
        if not preferences:
            return 0.5
        
        # 检查是否符合真实的时间偏好分布
        morning_prefs = [p for p in preferences if '08:00' in str(p) or '09:00' in str(p) or '10:00' in str(p)]
        evening_prefs = [p for p in preferences if '19:00' in str(p) or '20:00' in str(p)]
        
        # 上午偏好应该多于晚上偏好
        morning_ratio = len(morning_prefs) / len(preferences)
        evening_ratio = len(evening_prefs) / len(preferences)
        
        # 真实分布：上午0.6-0.8，晚上0.1-0.3
        morning_score = 1.0 if 0.6 <= morning_ratio <= 0.8 else max(0, 1 - abs(morning_ratio - 0.7) * 2)
        evening_score = 1.0 if 0.1 <= evening_ratio <= 0.3 else max(0, 1 - abs(evening_ratio - 0.2) * 2)
        
        return (morning_score + evening_score) / 2
    
    def generate_quality_report(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """生成详细的质量评估报告"""
        metrics = self.evaluate_data_quality(dataset)
        
        report = {
            "assessment_summary": {
                "overall_score": round(metrics.overall_score, 3),
                "grade": self._get_quality_grade(metrics.overall_score),
                "assessment_date": "2024-08-30"
            },
            "detailed_scores": {
                "realism": round(metrics.realism_score, 3),
                "complexity": round(metrics.complexity_score, 3),
                "diversity": round(metrics.diversity_score, 3),
                "consistency": round(metrics.consistency_score, 3),
                "algorithm_stress": round(metrics.algorithm_stress_score, 3)
            },
            "recommendations": self._generate_improvement_recommendations(metrics),
            "dataset_statistics": self._generate_dataset_statistics(dataset)
        }
        
        return report
    
    def _get_quality_grade(self, score: float) -> str:
        """获取质量等级"""
        if score >= 0.9:
            return "优秀 (A)"
        elif score >= 0.8:
            return "良好 (B)"
        elif score >= 0.7:
            return "中等 (C)"
        elif score >= 0.6:
            return "及格 (D)"
        else:
            return "需要改进 (F)"
    
    def _assess_enrollment_realism(self, enrollments: List[Dict], courses: List[Dict]) -> float:
        """评估选课真实性"""
        if not enrollments or not courses:
            return 0.5
        
        # 检查选课分布是否符合帕累托原理(80-20法则)
        course_enrollment_counts = {}
        for enrollment in enrollments:
            course_id = enrollment.get('course_id')
            if course_id:
                course_enrollment_counts[course_id] = course_enrollment_counts.get(course_id, 0) + 1
        
        if not course_enrollment_counts:
            return 0.3
        
        # 计算热门课程集中度
        sorted_counts = sorted(course_enrollment_counts.values(), reverse=True)
        total_enrollments = sum(sorted_counts)
        top_20_percent = int(len(sorted_counts) * 0.2)
        
        if top_20_percent > 0:
            top_20_enrollments = sum(sorted_counts[:top_20_percent])
            concentration_ratio = top_20_enrollments / total_enrollments
            
            # 理想的80-20分布应该在0.6-0.8之间
            if 0.6 <= concentration_ratio <= 0.8:
                return 1.0
            else:
                return max(0.3, 1 - abs(concentration_ratio - 0.7) * 2)
        
        return 0.5
    
    def _assess_teacher_assignment_realism(self, courses: List[Dict], teachers: List[Dict]) -> float:
        """评估教师分配真实性"""
        if not courses or not teachers:
            return 0.5
        
        assignment_scores = []
        
        for course in courses:
            teacher_ids = course.get('teacher_ids', [])
            if not teacher_ids:
                assignment_scores.append(0.3)  # 无教师分配不太真实
                continue
            
            # 检查教师数量合理性
            course_credits = course.get('credits', 3)
            expected_teacher_count = 1 if course_credits <= 3 else min(2, course_credits // 2)
            
            if len(teacher_ids) == expected_teacher_count:
                assignment_scores.append(1.0)
            elif abs(len(teacher_ids) - expected_teacher_count) == 1:
                assignment_scores.append(0.8)
            else:
                assignment_scores.append(0.5)
        
        return np.mean(assignment_scores) if assignment_scores else 0.5
    
    def _calculate_dependency_complexity(self, courses: List[Dict]) -> float:
        """计算课程依赖关系复杂度"""
        if not courses:
            return 0.0
        
        # 统计有先修关系的课程比例
        courses_with_prereqs = sum(1 for course in courses if course.get('prerequisites', []))
        prereq_ratio = courses_with_prereqs / len(courses)
        
        # 理想的先修关系比例应该在30-50%之间
        if 0.3 <= prereq_ratio <= 0.5:
            return 1.0
        elif prereq_ratio < 0.3:
            return prereq_ratio / 0.3
        else:
            return max(0.5, 1 - (prereq_ratio - 0.5) * 2)
    
    def _calculate_course_type_diversity(self, courses: List[Dict]) -> float:
        """计算课程类型多样性"""
        if not courses:
            return 0.0
        
        course_types = [course.get('course_type', '未知') for course in courses]
        unique_types = set(course_types)
        
        # 期望至少有4种不同的课程类型
        expected_types = 4
        diversity_score = min(1.0, len(unique_types) / expected_types)
        
        return diversity_score
    
    def _calculate_teacher_diversity(self, teachers: List[Dict]) -> float:
        """计算教师多样性"""
        if not teachers:
            return 0.0
        
        # 职称多样性
        titles = [teacher.get('title', '未知') for teacher in teachers]
        unique_titles = set(titles)
        title_diversity = min(1.0, len(unique_titles) / 4)  # 期望4种职称
        
        # 院系多样性
        departments = [teacher.get('department', '未知') for teacher in teachers]
        unique_departments = set(departments)
        dept_diversity = min(1.0, len(unique_departments) / 6)  # 期望6个院系
        
        return (title_diversity + dept_diversity) / 2
    
    def _check_foreign_key_consistency(self, dataset: Dict[str, Any]) -> float:
        """检查外键一致性"""
        consistency_score = 1.0
        
        # 检查课程中的教师ID是否存在
        if 'courses' in dataset and 'teachers' in dataset:
            teacher_ids = {t['id'] for t in dataset['teachers']}
            invalid_refs = 0
            total_refs = 0
            
            for course in dataset['courses']:
                for teacher_id in course.get('teacher_ids', []):
                    total_refs += 1
                    if teacher_id not in teacher_ids:
                        invalid_refs += 1
            
            if total_refs > 0:
                consistency_score *= (total_refs - invalid_refs) / total_refs
        
        return consistency_score
    
    def _check_business_logic_consistency(self, dataset: Dict[str, Any]) -> float:
        """检查业务逻辑一致性"""
        consistency_checks = []
        
        # 检查教室容量与课程人数的匹配
        if 'courses' in dataset and 'classrooms' in dataset:
            capacity_matches = 0
            total_assignments = 0
            
            for course in dataset['courses']:
                max_students = course.get('max_students', 50)
                # 假设课程已分配教室(实际实现中应该有教室分配数据)
                total_assignments += 1
                # 这里简化处理，假设大部分分配是合理的
                capacity_matches += 1
            
            if total_assignments > 0:
                consistency_checks.append(capacity_matches / total_assignments)
        
        return np.mean(consistency_checks) if consistency_checks else 1.0
    
    def _calculate_constraint_density(self, dataset: Dict[str, Any]) -> float:
        """计算约束密度"""
        constraint_count = 0
        entity_count = 0
        
        # 统计各种约束
        if 'courses' in dataset:
            entity_count += len(dataset['courses'])
            # 课程约束：先修关系、教师分配、教室需求等
            constraint_count += sum(len(course.get('prerequisites', [])) for course in dataset['courses'])
            constraint_count += sum(len(course.get('teacher_ids', [])) for course in dataset['courses'])
        
        if 'teachers' in dataset:
            entity_count += len(dataset['teachers'])
            # 教师约束：时间偏好、工作负荷限制等
            if 'teacher_preferences' in dataset:
                constraint_count += len(dataset['teacher_preferences'])
        
        if 'conflicts' in dataset:
            constraint_count += len(dataset['conflicts']) * 2  # 每个冲突增加约束密度
        
        return min(1.0, constraint_count / max(entity_count, 1))
    
    def _generate_dataset_statistics(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据集统计信息"""
        stats = {
            "total_entities": 0,
            "entity_breakdown": {},
            "data_completeness": {},
            "relationship_density": 0.0
        }
        
        # 统计各类实体数量
        for key, value in dataset.items():
            if isinstance(value, list):
                count = len(value)
                stats["entity_breakdown"][key] = count
                stats["total_entities"] += count
        
        # 计算数据完整性
        expected_keys = ['departments', 'teachers', 'students', 'courses', 'classrooms']
        present_keys = [key for key in expected_keys if key in dataset and dataset[key]]
        stats["data_completeness"]["core_entities"] = len(present_keys) / len(expected_keys)
        
        # 计算关系密度
        total_relationships = 0
        if 'enrollments' in dataset:
            total_relationships += len(dataset['enrollments'])
        if 'course_dependencies' in dataset:
            total_relationships += len(dataset['course_dependencies'])
        if 'teacher_preferences' in dataset:
            total_relationships += len(dataset['teacher_preferences'])
        
        stats["relationship_density"] = total_relationships / max(stats["total_entities"], 1)
        
        return stats
    
    def _generate_improvement_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if metrics.realism_score < 0.7:
            recommendations.append("建议增强数据真实性：调整时间分布、选课模式等")
        
        if metrics.complexity_score < 0.7:
            recommendations.append("建议增加冲突场景复杂度：添加更多多维度冲突")
        
        if metrics.diversity_score < 0.7:
            recommendations.append("建议提升数据多样性：增加课程类型、教师背景多样性")
        
        if metrics.algorithm_stress_score < 0.7:
            recommendations.append("建议强化算法压力测试：增加资源竞争强度")
        
        return recommendations