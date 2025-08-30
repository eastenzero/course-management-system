# file: algorithms/conflict/analyzer.py
# 功能: 冲突分析器

import logging
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
import numpy as np
from ..models import Assignment, Conflict

logger = logging.getLogger(__name__)


class ConflictAnalyzer:
    """冲突分析器"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_conflicts(self, conflicts: List[Conflict], assignments: List[Assignment],
                         courses: List[Dict] = None, teachers: List[Dict] = None,
                         classrooms: List[Dict] = None) -> Dict[str, Any]:
        """全面分析冲突"""
        analysis = {
            'summary': self._analyze_conflict_summary(conflicts),
            'patterns': self._analyze_conflict_patterns(conflicts),
            'hotspots': self._analyze_conflict_hotspots(conflicts, assignments),
            'severity_distribution': self._analyze_severity_distribution(conflicts),
            'time_distribution': self._analyze_time_distribution(conflicts),
            'resource_conflicts': self._analyze_resource_conflicts(conflicts, teachers, classrooms),
            'recommendations': self._generate_recommendations(conflicts, assignments),
        }
        
        if courses:
            analysis['course_analysis'] = self._analyze_course_conflicts(conflicts, courses)
        
        if teachers:
            analysis['teacher_analysis'] = self._analyze_teacher_conflicts(conflicts, teachers)
        
        if classrooms:
            analysis['classroom_analysis'] = self._analyze_classroom_conflicts(conflicts, classrooms)
        
        return analysis
    
    def _analyze_conflict_summary(self, conflicts: List[Conflict]) -> Dict[str, Any]:
        """分析冲突摘要"""
        if not conflicts:
            return {
                'total_conflicts': 0,
                'conflict_types': {},
                'severity_counts': {},
                'average_assignments_per_conflict': 0,
            }
        
        conflict_types = Counter(c.conflict_type for c in conflicts)
        severity_counts = Counter(c.severity for c in conflicts)
        total_assignments = sum(len(c.assignments) for c in conflicts)
        
        return {
            'total_conflicts': len(conflicts),
            'conflict_types': dict(conflict_types),
            'severity_counts': dict(severity_counts),
            'average_assignments_per_conflict': total_assignments / len(conflicts),
            'most_common_type': conflict_types.most_common(1)[0] if conflict_types else None,
            'most_common_severity': severity_counts.most_common(1)[0] if severity_counts else None,
        }
    
    def _analyze_conflict_patterns(self, conflicts: List[Conflict]) -> Dict[str, Any]:
        """分析冲突模式"""
        patterns = {
            'recurring_conflicts': self._find_recurring_conflicts(conflicts),
            'cascade_conflicts': self._find_cascade_conflicts(conflicts),
            'cluster_conflicts': self._find_cluster_conflicts(conflicts),
        }
        
        return patterns
    
    def _find_recurring_conflicts(self, conflicts: List[Conflict]) -> List[Dict[str, Any]]:
        """查找重复出现的冲突"""
        # 按冲突特征分组
        conflict_signatures = defaultdict(list)
        
        for conflict in conflicts:
            # 创建冲突签名
            if conflict.conflict_type == 'teacher_time':
                teacher_ids = set(a.teacher_id for a in conflict.assignments)
                time_slots = set((a.day_of_week, a.time_slot) for a in conflict.assignments)
                signature = f"teacher_time:{sorted(teacher_ids)}:{sorted(time_slots)}"
            elif conflict.conflict_type == 'classroom_time':
                classroom_ids = set(a.classroom_id for a in conflict.assignments)
                time_slots = set((a.day_of_week, a.time_slot) for a in conflict.assignments)
                signature = f"classroom_time:{sorted(classroom_ids)}:{sorted(time_slots)}"
            else:
                signature = f"{conflict.conflict_type}:{len(conflict.assignments)}"
            
            conflict_signatures[signature].append(conflict)
        
        # 找到重复的冲突
        recurring = []
        for signature, conflict_list in conflict_signatures.items():
            if len(conflict_list) > 1:
                recurring.append({
                    'signature': signature,
                    'count': len(conflict_list),
                    'conflicts': conflict_list,
                })
        
        return sorted(recurring, key=lambda x: x['count'], reverse=True)
    
    def _find_cascade_conflicts(self, conflicts: List[Conflict]) -> List[Dict[str, Any]]:
        """查找级联冲突"""
        # 查找涉及相同资源的不同类型冲突
        resource_conflicts = defaultdict(list)
        
        for conflict in conflicts:
            for assignment in conflict.assignments:
                # 按教师分组
                resource_conflicts[f"teacher_{assignment.teacher_id}"].append(conflict)
                # 按教室分组
                resource_conflicts[f"classroom_{assignment.classroom_id}"].append(conflict)
                # 按时间分组
                resource_conflicts[f"time_{assignment.day_of_week}_{assignment.time_slot}"].append(conflict)
        
        cascades = []
        for resource, conflict_list in resource_conflicts.items():
            if len(conflict_list) > 1:
                # 检查是否有不同类型的冲突
                conflict_types = set(c.conflict_type for c in conflict_list)
                if len(conflict_types) > 1:
                    cascades.append({
                        'resource': resource,
                        'conflict_count': len(conflict_list),
                        'conflict_types': list(conflict_types),
                        'conflicts': conflict_list,
                    })
        
        return sorted(cascades, key=lambda x: x['conflict_count'], reverse=True)
    
    def _find_cluster_conflicts(self, conflicts: List[Conflict]) -> List[Dict[str, Any]]:
        """查找聚集性冲突"""
        # 按时间段分组冲突
        time_clusters = defaultdict(list)
        
        for conflict in conflicts:
            for assignment in conflict.assignments:
                time_key = (assignment.day_of_week, assignment.time_slot)
                time_clusters[time_key].append(conflict)
        
        clusters = []
        for time_key, conflict_list in time_clusters.items():
            if len(conflict_list) > 2:  # 3个或以上冲突认为是聚集
                clusters.append({
                    'time_slot': time_key,
                    'day_name': ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'][time_key[0]],
                    'conflict_count': len(conflict_list),
                    'unique_conflicts': len(set(c.conflict_key for c in conflict_list)),
                    'conflicts': conflict_list,
                })
        
        return sorted(clusters, key=lambda x: x['conflict_count'], reverse=True)
    
    def _analyze_conflict_hotspots(self, conflicts: List[Conflict], 
                                 assignments: List[Assignment]) -> Dict[str, Any]:
        """分析冲突热点"""
        # 时间热点
        time_conflicts = defaultdict(int)
        for conflict in conflicts:
            for assignment in conflict.assignments:
                time_key = (assignment.day_of_week, assignment.time_slot)
                time_conflicts[time_key] += 1
        
        # 教师热点
        teacher_conflicts = defaultdict(int)
        for conflict in conflicts:
            for assignment in conflict.assignments:
                teacher_conflicts[assignment.teacher_id] += 1
        
        # 教室热点
        classroom_conflicts = defaultdict(int)
        for conflict in conflicts:
            for assignment in conflict.assignments:
                classroom_conflicts[assignment.classroom_id] += 1
        
        return {
            'time_hotspots': sorted(time_conflicts.items(), key=lambda x: x[1], reverse=True)[:10],
            'teacher_hotspots': sorted(teacher_conflicts.items(), key=lambda x: x[1], reverse=True)[:10],
            'classroom_hotspots': sorted(classroom_conflicts.items(), key=lambda x: x[1], reverse=True)[:10],
        }
    
    def _analyze_severity_distribution(self, conflicts: List[Conflict]) -> Dict[str, Any]:
        """分析严重性分布"""
        severity_counts = Counter(c.severity for c in conflicts)
        total_conflicts = len(conflicts)
        
        distribution = {}
        for severity in ['high', 'medium', 'low']:
            count = severity_counts.get(severity, 0)
            distribution[severity] = {
                'count': count,
                'percentage': (count / total_conflicts * 100) if total_conflicts > 0 else 0,
            }
        
        return distribution
    
    def _analyze_time_distribution(self, conflicts: List[Conflict]) -> Dict[str, Any]:
        """分析时间分布"""
        day_conflicts = defaultdict(int)
        hour_conflicts = defaultdict(int)
        
        for conflict in conflicts:
            for assignment in conflict.assignments:
                day_conflicts[assignment.day_of_week] += 1
                hour_conflicts[assignment.time_slot] += 1
        
        # 转换为更友好的格式
        day_names = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
        day_distribution = {
            day_names[day]: count for day, count in day_conflicts.items()
        }
        
        return {
            'by_day': day_distribution,
            'by_time_slot': dict(hour_conflicts),
            'peak_day': max(day_conflicts.items(), key=lambda x: x[1]) if day_conflicts else None,
            'peak_time_slot': max(hour_conflicts.items(), key=lambda x: x[1]) if hour_conflicts else None,
        }
    
    def _analyze_resource_conflicts(self, conflicts: List[Conflict],
                                  teachers: List[Dict] = None,
                                  classrooms: List[Dict] = None) -> Dict[str, Any]:
        """分析资源冲突"""
        analysis = {}
        
        if teachers:
            teacher_dict = {t['id']: t for t in teachers}
            teacher_conflict_analysis = defaultdict(list)
            
            for conflict in conflicts:
                if conflict.conflict_type == 'teacher_time':
                    for assignment in conflict.assignments:
                        teacher_id = assignment.teacher_id
                        teacher = teacher_dict.get(teacher_id, {})
                        teacher_conflict_analysis[teacher_id].append({
                            'conflict': conflict,
                            'teacher_name': teacher.get('name', f'Teacher {teacher_id}'),
                            'department': teacher.get('department', 'Unknown'),
                        })
            
            analysis['teacher_conflicts'] = dict(teacher_conflict_analysis)
        
        if classrooms:
            classroom_dict = {c['id']: c for c in classrooms}
            classroom_conflict_analysis = defaultdict(list)
            
            for conflict in conflicts:
                if conflict.conflict_type == 'classroom_time':
                    for assignment in conflict.assignments:
                        classroom_id = assignment.classroom_id
                        classroom = classroom_dict.get(classroom_id, {})
                        classroom_conflict_analysis[classroom_id].append({
                            'conflict': conflict,
                            'classroom_name': classroom.get('name', f'Classroom {classroom_id}'),
                            'capacity': classroom.get('capacity', 0),
                            'building': classroom.get('building', 'Unknown'),
                        })
            
            analysis['classroom_conflicts'] = dict(classroom_conflict_analysis)
        
        return analysis
    
    def _analyze_course_conflicts(self, conflicts: List[Conflict], 
                                courses: List[Dict]) -> Dict[str, Any]:
        """分析课程冲突"""
        course_dict = {c['id']: c for c in courses}
        course_conflicts = defaultdict(list)
        
        for conflict in conflicts:
            for assignment in conflict.assignments:
                course_id = assignment.course_id
                course = course_dict.get(course_id, {})
                course_conflicts[course_id].append({
                    'conflict': conflict,
                    'course_name': course.get('name', f'Course {course_id}'),
                    'course_type': course.get('course_type', 'Unknown'),
                    'credits': course.get('credits', 0),
                    'max_students': course.get('max_students', 0),
                })
        
        return dict(course_conflicts)
    
    def _analyze_teacher_conflicts(self, conflicts: List[Conflict],
                                 teachers: List[Dict]) -> Dict[str, Any]:
        """分析教师冲突"""
        teacher_dict = {t['id']: t for t in teachers}
        teacher_stats = defaultdict(lambda: {'conflicts': 0, 'workload': 0})
        
        for conflict in conflicts:
            for assignment in conflict.assignments:
                teacher_id = assignment.teacher_id
                teacher_stats[teacher_id]['conflicts'] += 1
        
        # 添加教师信息
        teacher_analysis = {}
        for teacher_id, stats in teacher_stats.items():
            teacher = teacher_dict.get(teacher_id, {})
            teacher_analysis[teacher_id] = {
                'name': teacher.get('name', f'Teacher {teacher_id}'),
                'department': teacher.get('department', 'Unknown'),
                'max_weekly_hours': teacher.get('max_weekly_hours', 20),
                'conflicts': stats['conflicts'],
            }
        
        return teacher_analysis
    
    def _analyze_classroom_conflicts(self, conflicts: List[Conflict],
                                   classrooms: List[Dict]) -> Dict[str, Any]:
        """分析教室冲突"""
        classroom_dict = {c['id']: c for c in classrooms}
        classroom_stats = defaultdict(lambda: {'conflicts': 0})
        
        for conflict in conflicts:
            for assignment in conflict.assignments:
                classroom_id = assignment.classroom_id
                classroom_stats[classroom_id]['conflicts'] += 1
        
        # 添加教室信息
        classroom_analysis = {}
        for classroom_id, stats in classroom_stats.items():
            classroom = classroom_dict.get(classroom_id, {})
            classroom_analysis[classroom_id] = {
                'name': classroom.get('name', f'Classroom {classroom_id}'),
                'capacity': classroom.get('capacity', 0),
                'room_type': classroom.get('room_type', 'Unknown'),
                'building': classroom.get('building', 'Unknown'),
                'conflicts': stats['conflicts'],
            }
        
        return classroom_analysis
    
    def _generate_recommendations(self, conflicts: List[Conflict],
                                assignments: List[Assignment]) -> List[Dict[str, Any]]:
        """生成解决建议"""
        recommendations = []
        
        # 基于冲突类型的建议
        conflict_types = Counter(c.conflict_type for c in conflicts)
        
        if conflict_types.get('teacher_time', 0) > 0:
            recommendations.append({
                'type': 'teacher_time',
                'priority': 'high',
                'title': '教师时间冲突解决建议',
                'description': '考虑调整教师工作量分配或增加教师资源',
                'actions': [
                    '重新分配部分课程到其他教师',
                    '调整课程时间安排',
                    '考虑增加兼职教师',
                ]
            })
        
        if conflict_types.get('classroom_time', 0) > 0:
            recommendations.append({
                'type': 'classroom_time',
                'priority': 'high',
                'title': '教室时间冲突解决建议',
                'description': '优化教室使用效率或增加教室资源',
                'actions': [
                    '重新分配教室使用时间',
                    '考虑使用其他可用教室',
                    '调整课程安排到非高峰时段',
                ]
            })
        
        if conflict_types.get('classroom_capacity', 0) > 0:
            recommendations.append({
                'type': 'classroom_capacity',
                'priority': 'medium',
                'title': '教室容量不足解决建议',
                'description': '调整教室分配以满足容量需求',
                'actions': [
                    '将大班课程安排到大教室',
                    '考虑分班教学',
                    '使用多媒体教室或阶梯教室',
                ]
            })
        
        return recommendations
    
    def export_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """导出分析报告"""
        report = []
        report.append("# 排课冲突分析报告\n")
        
        # 摘要
        summary = analysis.get('summary', {})
        report.append("## 冲突摘要")
        report.append(f"- 总冲突数: {summary.get('total_conflicts', 0)}")
        report.append(f"- 平均每冲突涉及分配数: {summary.get('average_assignments_per_conflict', 0):.2f}")
        
        # 冲突类型分布
        conflict_types = summary.get('conflict_types', {})
        if conflict_types:
            report.append("\n### 冲突类型分布")
            for conflict_type, count in conflict_types.items():
                report.append(f"- {conflict_type}: {count}")
        
        # 严重性分布
        severity_dist = analysis.get('severity_distribution', {})
        if severity_dist:
            report.append("\n### 严重性分布")
            for severity, data in severity_dist.items():
                report.append(f"- {severity}: {data.get('count', 0)} ({data.get('percentage', 0):.1f}%)")
        
        # 建议
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            report.append("\n## 解决建议")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"\n### {i}. {rec.get('title', '建议')}")
                report.append(f"优先级: {rec.get('priority', 'medium')}")
                report.append(f"描述: {rec.get('description', '')}")
                actions = rec.get('actions', [])
                if actions:
                    report.append("行动项:")
                    for action in actions:
                        report.append(f"- {action}")
        
        return "\n".join(report)
