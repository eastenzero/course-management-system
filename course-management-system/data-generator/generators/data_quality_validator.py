# file: data-generator/generators/data_quality_validator.py
# 功能: 数据质量验证和评估系统

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import statistics
import re
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

from course_scheduling_constraints import (
    CourseType, DifficultyLevel, TeacherTitle, TimeSlot,
    CourseRealismValidator
)


class QualityDimension(Enum):
    """质量维度"""
    COMPLETENESS = "完整性"        # 数据完整性
    CONSISTENCY = "一致性"         # 数据一致性
    ACCURACY = "准确性"           # 数据准确性
    VALIDITY = "有效性"           # 数据有效性
    UNIQUENESS = "唯一性"         # 数据唯一性
    REALISM = "真实性"            # 数据真实性
    CONSTRAINT_COMPLIANCE = "约束合规性"  # 约束遵循


class SeverityLevel(Enum):
    """严重程度"""
    CRITICAL = "严重"
    HIGH = "高"
    MEDIUM = "中等"
    LOW = "低"
    INFO = "信息"


@dataclass
class QualityIssue:
    """质量问题"""
    dimension: QualityDimension
    severity: SeverityLevel
    description: str
    affected_records: List[str]
    suggested_fix: str
    detection_rule: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QualityMetrics:
    """质量指标"""
    dimension: QualityDimension
    score: float  # 0-1 分数
    total_records: int
    valid_records: int
    issue_count: int
    issues: List[QualityIssue] = field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        """通过率"""
        return self.valid_records / max(1, self.total_records)


@dataclass
class QualityReport:
    """质量报告"""
    overall_score: float
    dimension_scores: Dict[QualityDimension, float]
    total_issues: int
    critical_issues: int
    metrics_by_dimension: Dict[QualityDimension, QualityMetrics]
    summary: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class CompletenessValidator:
    """完整性验证器"""
    
    def __init__(self):
        self.required_fields = {
            'teachers': ['teacher_id', 'name', 'title', 'department'],
            'courses': ['course_id', 'name', 'type', 'credits', 'department'],
            'schedules': ['course_id', 'teacher_id', 'classroom_id', 'time_slot'],
            'students': ['student_id', 'name', 'major', 'enrollment_year'],
            'departments': ['department_id', 'name']
        }
        
    def validate(self, data: Dict[str, List[Dict]]) -> QualityMetrics:
        """验证完整性"""
        issues = []
        total_records = 0
        valid_records = 0
        
        for data_type, records in data.items():
            if data_type not in self.required_fields:
                continue
                
            required = self.required_fields[data_type]
            total_records += len(records)
            
            for i, record in enumerate(records):
                missing_fields = [field for field in required if not record.get(field)]
                
                if missing_fields:
                    issues.append(QualityIssue(
                        dimension=QualityDimension.COMPLETENESS,
                        severity=SeverityLevel.HIGH,
                        description=f"{data_type}记录缺少必要字段: {missing_fields}",
                        affected_records=[f"{data_type}[{i}]"],
                        suggested_fix=f"补充缺失的字段: {missing_fields}",
                        detection_rule="required_fields_check"
                    ))
                else:
                    valid_records += 1
                    
        score = valid_records / max(1, total_records)
        
        return QualityMetrics(
            dimension=QualityDimension.COMPLETENESS,
            score=score,
            total_records=total_records,
            valid_records=valid_records,
            issue_count=len(issues),
            issues=issues
        )


class ConsistencyValidator:
    """一致性验证器"""
    
    def validate(self, data: Dict[str, List[Dict]]) -> QualityMetrics:
        """验证一致性"""
        issues = []
        total_checks = 0
        valid_checks = 0
        
        # 检查外键一致性
        issues.extend(self._check_foreign_key_consistency(data))
        
        # 检查数据类型一致性
        issues.extend(self._check_data_type_consistency(data))
        
        # 检查枚举值一致性
        issues.extend(self._check_enum_consistency(data))
        
        # 检查业务逻辑一致性
        issues.extend(self._check_business_logic_consistency(data))
        
        # 计算总体一致性得分
        total_checks = sum(len(records) for records in data.values())
        valid_checks = total_checks - len(issues)
        
        score = valid_checks / max(1, total_checks)
        
        return QualityMetrics(
            dimension=QualityDimension.CONSISTENCY,
            score=score,
            total_records=total_checks,
            valid_records=valid_checks,
            issue_count=len(issues),
            issues=issues
        )
        
    def _check_foreign_key_consistency(self, data: Dict[str, List[Dict]]) -> List[QualityIssue]:
        """检查外键一致性"""
        issues = []
        
        # 创建ID集合
        teacher_ids = {t.get('teacher_id') for t in data.get('teachers', []) if t.get('teacher_id')}
        course_ids = {c.get('course_id') for c in data.get('courses', []) if c.get('course_id')}
        
        # 检查排课表中的外键
        for i, schedule in enumerate(data.get('schedules', [])):
            if schedule.get('teacher_id') and schedule['teacher_id'] not in teacher_ids:
                issues.append(QualityIssue(
                    dimension=QualityDimension.CONSISTENCY,
                    severity=SeverityLevel.CRITICAL,
                    description=f"排课记录引用了不存在的教师ID: {schedule['teacher_id']}",
                    affected_records=[f"schedules[{i}]"],
                    suggested_fix="检查教师ID是否正确或添加对应的教师记录",
                    detection_rule="foreign_key_teacher_id"
                ))
                
            if schedule.get('course_id') and schedule['course_id'] not in course_ids:
                issues.append(QualityIssue(
                    dimension=QualityDimension.CONSISTENCY,
                    severity=SeverityLevel.CRITICAL,
                    description=f"排课记录引用了不存在的课程ID: {schedule['course_id']}",
                    affected_records=[f"schedules[{i}]"],
                    suggested_fix="检查课程ID是否正确或添加对应的课程记录",
                    detection_rule="foreign_key_course_id"
                ))
                
        return issues
        
    def _check_data_type_consistency(self, data: Dict[str, List[Dict]]) -> List[QualityIssue]:
        """检查数据类型一致性"""
        issues = []
        
        type_expectations = {
            'teachers': {
                'experience_years': int,
                'max_courses_per_semester': int,
                'average_evaluation': (int, float)
            },
            'courses': {
                'credits': int,
                'weekly_hours': int,
                'total_hours': int,
                'student_capacity': int
            }
        }
        
        for data_type, records in data.items():
            if data_type not in type_expectations:
                continue
                
            expected_types = type_expectations[data_type]
            
            for i, record in enumerate(records):
                for field, expected_type in expected_types.items():
                    if field in record and record[field] is not None:
                        value = record[field]
                        
                        if isinstance(expected_type, tuple):
                            if not isinstance(value, expected_type):
                                issues.append(QualityIssue(
                                    dimension=QualityDimension.CONSISTENCY,
                                    severity=SeverityLevel.MEDIUM,
                                    description=f"{data_type}[{i}].{field} 类型错误",
                                    affected_records=[f"{data_type}[{i}]"],
                                    suggested_fix=f"将 {field} 转换为正确的数据类型",
                                    detection_rule="data_type_check"
                                ))
                        else:
                            if not isinstance(value, expected_type):
                                issues.append(QualityIssue(
                                    dimension=QualityDimension.CONSISTENCY,
                                    severity=SeverityLevel.MEDIUM,
                                    description=f"{data_type}[{i}].{field} 类型错误",
                                    affected_records=[f"{data_type}[{i}]"],
                                    suggested_fix=f"将 {field} 转换为正确类型",
                                    detection_rule="data_type_check"
                                ))
                                
        return issues
        
    def _check_enum_consistency(self, data: Dict[str, List[Dict]]) -> List[QualityIssue]:
        """检查枚举值一致性"""
        issues = []
        
        enum_fields = {
            'teachers': {
                'title': [title.value for title in TeacherTitle]
            },
            'courses': {
                'type': [course_type.value for course_type in CourseType]
            }
        }
        
        for data_type, records in data.items():
            if data_type not in enum_fields:
                continue
                
            field_enums = enum_fields[data_type]
            
            for i, record in enumerate(records):
                for field, valid_values in field_enums.items():
                    if field in record and record[field] is not None:
                        value = record[field]
                        
                        if value not in valid_values:
                            issues.append(QualityIssue(
                                dimension=QualityDimension.CONSISTENCY,
                                severity=SeverityLevel.HIGH,
                                description=f"{data_type}[{i}].{field} 值无效: '{value}'",
                                affected_records=[f"{data_type}[{i}]"],
                                suggested_fix=f"将 {field} 设置为有效值",
                                detection_rule="enum_value_check"
                            ))
                            
        return issues
        
    def _check_business_logic_consistency(self, data: Dict[str, List[Dict]]) -> List[QualityIssue]:
        """检查业务逻辑一致性"""
        issues = []
        
        # 检查课程学分与学时的合理性
        for i, course in enumerate(data.get('courses', [])):
            credits = course.get('credits', 0)
            total_hours = course.get('total_hours', 0)
            
            if credits > 0 and total_hours > 0:
                expected_hours = credits * 16
                hour_ratio = total_hours / expected_hours
                
                if hour_ratio < 0.8 or hour_ratio > 1.5:
                    issues.append(QualityIssue(
                        dimension=QualityDimension.CONSISTENCY,
                        severity=SeverityLevel.MEDIUM,
                        description=f"课程学分与学时比例异常",
                        affected_records=[f"courses[{i}]"],
                        suggested_fix="调整学分或学时使其符合标准",
                        detection_rule="credit_hour_ratio_check"
                    ))
                    
        return issues


class DataQualityAssessment:
    """数据质量评估系统"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validators = {
            QualityDimension.COMPLETENESS: CompletenessValidator(),
            QualityDimension.CONSISTENCY: ConsistencyValidator()
        }
        
    def assess_quality(self, data: Dict[str, List[Dict]], 
                      sampling_rate: float = 1.0) -> QualityReport:
        """评估数据质量"""
        self.logger.info("开始数据质量评估...")
        
        # 应用采样
        sampled_data = self._apply_sampling(data, sampling_rate)
        
        # 执行各维度验证
        metrics_by_dimension = {}
        all_issues = []
        
        for dimension, validator in self.validators.items():
            try:
                metrics = validator.validate(sampled_data)
                metrics_by_dimension[dimension] = metrics
                all_issues.extend(metrics.issues)
                
                self.logger.info(f"{dimension.value} 验证完成: 得分 {metrics.score:.3f}")
                
            except Exception as e:
                self.logger.error(f"{dimension.value} 验证失败: {e}")
                
        # 计算总体得分
        dimension_scores = {d: m.score for d, m in metrics_by_dimension.items()}
        overall_score = statistics.mean(dimension_scores.values()) if dimension_scores else 0.0
        
        # 统计问题
        critical_issues = len([i for i in all_issues if i.severity == SeverityLevel.CRITICAL])
        
        # 生成建议
        recommendations = self._generate_recommendations(all_issues, metrics_by_dimension)
        
        # 创建摘要
        summary = {
            'total_records': sum(len(records) for records in data.values()),
            'data_types': list(data.keys()),
            'validation_coverage': len(metrics_by_dimension),
            'sampling_rate': sampling_rate
        }
        
        return QualityReport(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            total_issues=len(all_issues),
            critical_issues=critical_issues,
            metrics_by_dimension=metrics_by_dimension,
            summary=summary,
            recommendations=recommendations
        )
        
    def _apply_sampling(self, data: Dict[str, List[Dict]], 
                       sampling_rate: float) -> Dict[str, List[Dict]]:
        """应用采样"""
        if sampling_rate >= 1.0:
            return data
            
        sampled_data = {}
        for data_type, records in data.items():
            sample_size = max(1, int(len(records) * sampling_rate))
            sampled_records = records[:sample_size]
            sampled_data[data_type] = sampled_records
            
        return sampled_data
        
    def _generate_recommendations(self, issues: List[QualityIssue], 
                                metrics: Dict[QualityDimension, QualityMetrics]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于问题严重程度的建议
        critical_count = len([i for i in issues if i.severity == SeverityLevel.CRITICAL])
        if critical_count > 0:
            recommendations.append(f"立即处理 {critical_count} 个严重问题")
            
        # 基于维度得分的建议
        for dimension, metric in metrics.items():
            if metric.score < 0.8:
                recommendations.append(f"改进{dimension.value}质量（当前得分: {metric.score:.2f}）")
                
        if not recommendations:
            recommendations.append("数据质量良好，继续保持")
            
        return recommendations