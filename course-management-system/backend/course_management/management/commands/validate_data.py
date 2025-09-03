import os
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Building, Classroom
from apps.schedules.models import Schedule, TimeSlot
from django.db.models import Count, Avg, Max, Min

User = get_user_model()

class Command(BaseCommand):
    help = '验证数据库数据的合理性'

    def handle(self, *args, **options):
        self.stdout.write("🔍 开始综合数据验证...")
        self.stdout.write("=" * 60)
        
        # 创建验证器实例并运行
        validator = ComprehensiveDataValidator()
        validator.run_validation()
        
        self.stdout.write(self.style.SUCCESS('数据验证完成！'))


class ComprehensiveDataValidator:
    """综合数据验证器"""
    
    def __init__(self):
        self.report = {
            'validation_time': datetime.now().isoformat(),
            'data_statistics': {},
            'hard_constraints': {},
            'soft_constraints': {},
            'data_quality': {},
            'recommendations': []
        }
    
    def run_validation(self):
        """运行完整的数据验证"""
        print("🔍 开始综合数据验证...")
        print("=" * 60)
        
        # 1. 数据统计
        self._collect_data_statistics()
        
        # 2. 硬约束验证
        self._validate_hard_constraints()
        
        # 3. 软约束评估
        self._evaluate_soft_constraints()
        
        # 4. 数据质量检查
        self._check_data_quality()
        
        # 5. 生成建议
        self._generate_recommendations()
        
        # 6. 输出报告
        self._output_report()
    
    def _collect_data_statistics(self):
        """收集数据统计信息"""
        print("📊 收集数据统计信息...")
        
        stats = {}
        
        # 基础数据统计
        stats['users'] = {
            'total': User.objects.count(),
            'students': User.objects.filter(user_type='student').count(),
            'teachers': User.objects.filter(user_type='teacher').count(),
            'admins': User.objects.filter(user_type='admin').count()
        }
        
        stats['infrastructure'] = {
            'buildings': Building.objects.count(),
            'classrooms': Classroom.objects.count(),
            'time_slots': TimeSlot.objects.count()
        }
        
        stats['academic'] = {
            'courses': Course.objects.count(),
            'active_courses': Course.objects.filter(is_active=True).count(),
            'schedules': Schedule.objects.count(),
            'active_schedules': Schedule.objects.filter(status='active').count(),
            'enrollments': Enrollment.objects.count(),
            'active_enrollments': Enrollment.objects.filter(is_active=True).count()
        }
        
        # 详细分析
        stats['course_analysis'] = {
            'by_type': dict(Course.objects.values('course_type').annotate(count=Count('id'))),
            'by_department': dict(Course.objects.values('department').annotate(count=Count('id'))),
            'avg_credits': Course.objects.aggregate(avg=Avg('credits'))['avg'] or 0,
            'avg_hours': Course.objects.aggregate(avg=Avg('hours'))['avg'] or 0
        }
        
        stats['enrollment_analysis'] = {
            'by_status': dict(Enrollment.objects.values('status').annotate(count=Count('id'))),
            'students_with_enrollments': Enrollment.objects.values('student').distinct().count(),
            'courses_with_enrollments': Enrollment.objects.values('course').distinct().count(),
            'avg_enrollments_per_student': None,
            'avg_enrollments_per_course': None
        }
        
        # 计算平均值
        if stats['users']['students'] > 0:
            stats['enrollment_analysis']['avg_enrollments_per_student'] = \
                stats['academic']['enrollments'] / stats['users']['students']
        
        if stats['academic']['courses'] > 0:
            stats['enrollment_analysis']['avg_enrollments_per_course'] = \
                stats['academic']['enrollments'] / stats['academic']['courses']
        
        self.report['data_statistics'] = stats
        print("✅ 数据统计收集完成")
    
    def _validate_hard_constraints(self):
        """验证硬约束"""
        print("🔒 验证硬约束...")
        
        violations = {}
        
        # 1. 教师时间冲突检查
        teacher_conflicts = self._check_teacher_time_conflicts()
        violations['teacher_time_conflicts'] = teacher_conflicts
        
        # 2. 教室时间冲突检查
        classroom_conflicts = self._check_classroom_time_conflicts()
        violations['classroom_time_conflicts'] = classroom_conflicts
        
        # 3. 教室容量约束检查
        capacity_violations = self._check_classroom_capacity()
        violations['capacity_violations'] = capacity_violations
        
        # 4. 数据完整性检查
        integrity_issues = self._check_data_integrity()
        violations['data_integrity_issues'] = integrity_issues
        
        self.report['hard_constraints'] = {
            'violations': violations,
            'total_violations': sum(
                len(v) if isinstance(v, list) else 
                sum(v.values()) if isinstance(v, dict) else v 
                for v in violations.values()
            ),
            'compliance_rate': self._calculate_compliance_rate(violations)
        }
        
        print(f"✅ 硬约束验证完成，发现 {self.report['hard_constraints']['total_violations']} 个违例")
    
    def _check_teacher_time_conflicts(self):
        """检查教师时间冲突"""
        conflicts = []
        
        # 查询同一教师在同一时间段的多个排课
        duplicate_schedules = Schedule.objects.values(
            'teacher', 'day_of_week', 'time_slot'
        ).annotate(
            count=Count('id')
        ).filter(
            count__gt=1,
            status='active'
        )
        
        for dup in duplicate_schedules:
            schedules = Schedule.objects.filter(
                teacher_id=dup['teacher'],
                day_of_week=dup['day_of_week'],
                time_slot_id=dup['time_slot'],
                status='active'
            )
            
            conflicts.append({
                'type': 'teacher_time_conflict',
                'teacher_id': dup['teacher'],
                'day_of_week': dup['day_of_week'],
                'time_slot_id': dup['time_slot'],
                'conflicting_schedules': [s.id for s in schedules],
                'count': dup['count']
            })
        
        return conflicts
    
    def _check_classroom_time_conflicts(self):
        """检查教室时间冲突"""
        conflicts = []
        
        # 查询同一教室在同一时间段的多个排课
        duplicate_schedules = Schedule.objects.values(
            'classroom', 'day_of_week', 'time_slot'
        ).annotate(
            count=Count('id')
        ).filter(
            count__gt=1,
            status='active'
        )
        
        for dup in duplicate_schedules:
            schedules = Schedule.objects.filter(
                classroom_id=dup['classroom'],
                day_of_week=dup['day_of_week'],
                time_slot_id=dup['time_slot'],
                status='active'
            )
            
            conflicts.append({
                'type': 'classroom_time_conflict',
                'classroom_id': dup['classroom'],
                'day_of_week': dup['day_of_week'],
                'time_slot_id': dup['time_slot'],
                'conflicting_schedules': [s.id for s in schedules],
                'count': dup['count']
            })
        
        return conflicts
    
    def _check_classroom_capacity(self):
        """检查教室容量约束"""
        violations = []
        
        # 查询选课人数超过教室容量的情况
        schedules = Schedule.objects.filter(status='active').select_related(
            'course', 'classroom'
        )
        
        for schedule in schedules:
            enrollment_count = Enrollment.objects.filter(
                course=schedule.course,
                status='enrolled'
            ).count()
            
            if enrollment_count > schedule.classroom.capacity:
                violations.append({
                    'type': 'capacity_violation',
                    'schedule_id': schedule.id,
                    'course_id': schedule.course.id,
                    'course_name': schedule.course.name,
                    'classroom_id': schedule.classroom.id,
                    'classroom_capacity': schedule.classroom.capacity,
                    'enrollment_count': enrollment_count,
                    'overflow': enrollment_count - schedule.classroom.capacity
                })
        
        return violations
    
    def _check_data_integrity(self):
        """检查数据完整性"""
        issues = {}
        
        # 检查课程没有教师的情况
        courses_without_teachers = Course.objects.filter(
            teachers__isnull=True
        ).count()
        issues['courses_without_teachers'] = courses_without_teachers
        
        # 检查课程没有排课的情况
        courses_without_schedules = Course.objects.filter(
            is_active=True,
            schedules__isnull=True
        ).count()
        issues['courses_without_schedules'] = courses_without_schedules
        
        # 检查排课没有选课的情况
        schedules_without_enrollments = Schedule.objects.filter(
            status='active'
        ).exclude(
            course__in=Enrollment.objects.values('course')
        ).count()
        issues['schedules_without_enrollments'] = schedules_without_enrollments
        
        # 检查孤立的选课记录
        orphaned_enrollments = Enrollment.objects.exclude(
            course__in=Schedule.objects.filter(status='active').values('course')
        ).count()
        issues['orphaned_enrollments'] = orphaned_enrollments
        
        return issues
    
    def _evaluate_soft_constraints(self):
        """评估软约束"""
        print("📈 评估软约束...")
        
        metrics = {}
        
        # 1. 教师工作量分布
        teacher_workload = self._analyze_teacher_workload()
        metrics['teacher_workload'] = teacher_workload
        
        # 2. 教室利用率分析
        classroom_utilization = self._analyze_classroom_utilization()
        metrics['classroom_utilization'] = classroom_utilization
        
        # 3. 时间分布分析
        time_distribution = self._analyze_time_distribution()
        metrics['time_distribution'] = time_distribution
        
        # 4. 选课分布分析
        enrollment_distribution = self._analyze_enrollment_distribution()
        metrics['enrollment_distribution'] = enrollment_distribution
        
        self.report['soft_constraints'] = metrics
        print("✅ 软约束评估完成")
    
    def _analyze_teacher_workload(self):
        """分析教师工作量"""
        workload_stats = Schedule.objects.filter(
            status='active'
        ).values('teacher').annotate(
            course_count=Count('course', distinct=True),
            total_schedules=Count('id')
        ).aggregate(
            avg_courses=Avg('course_count'),
            max_courses=Max('course_count'),
            min_courses=Min('course_count'),
            avg_schedules=Avg('total_schedules'),
            max_schedules=Max('total_schedules')
        )
        
        # 工作量分布
        workload_distribution = {}
        workload_ranges = [(0, 5), (6, 10), (11, 15), (16, 20), (21, 50)]
        
        for min_load, max_load in workload_ranges:
            count = Schedule.objects.filter(
                status='active'
            ).values('teacher').annotate(
                schedule_count=Count('id')
            ).filter(
                schedule_count__gte=min_load,
                schedule_count__lte=max_load
            ).count()
            
            workload_distribution[f"{min_load}-{max_load}"] = count
        
        return {
            'statistics': workload_stats,
            'distribution': workload_distribution
        }
    
    def _analyze_classroom_utilization(self):
        """分析教室利用率"""
        total_classrooms = Classroom.objects.filter(is_available=True).count()
        used_classrooms = Schedule.objects.filter(
            status='active'
        ).values('classroom').distinct().count()
        
        utilization_rate = (used_classrooms / total_classrooms * 100) if total_classrooms > 0 else 0
        
        # 按教室类型分析
        utilization_by_type = {}
        room_types = Classroom.objects.values('room_type').distinct()
        
        for room_type in room_types:
            total_type = Classroom.objects.filter(
                room_type=room_type['room_type'],
                is_available=True
            ).count()
            
            used_type = Schedule.objects.filter(
                status='active',
                classroom__room_type=room_type['room_type']
            ).values('classroom').distinct().count()
            
            utilization_by_type[room_type['room_type']] = {
                'total': total_type,
                'used': used_type,
                'rate': (used_type / total_type * 100) if total_type > 0 else 0
            }
        
        return {
            'overall_rate': utilization_rate,
            'total_classrooms': total_classrooms,
            'used_classrooms': used_classrooms,
            'by_type': utilization_by_type
        }
    
    def _analyze_time_distribution(self):
        """分析时间分布"""
        # 按星期分布
        weekly_distribution = dict(
            Schedule.objects.filter(status='active')
            .values('day_of_week')
            .annotate(count=Count('id'))
        )
        
        # 按时间段分布
        timeslot_distribution = dict(
            Schedule.objects.filter(status='active')
            .values('time_slot__name')
            .annotate(count=Count('id'))
        )
        
        return {
            'weekly': weekly_distribution,
            'timeslot': timeslot_distribution
        }
    
    def _analyze_enrollment_distribution(self):
        """分析选课分布"""
        # 按课程类型分布
        by_course_type = dict(
            Enrollment.objects.filter(is_active=True)
            .values('course__course_type')
            .annotate(count=Count('id'))
        )
        
        # 按状态分布
        by_status = dict(
            Enrollment.objects.values('status')
            .annotate(count=Count('id'))
        )
        
        # 课程容量使用率
        course_fill_rates = []
        courses_with_schedules = Course.objects.filter(
            schedules__status='active'
        ).distinct()
        
        for course in courses_with_schedules[:100]:  # 抽样分析
            enrollment_count = Enrollment.objects.filter(
                course=course,
                status='enrolled'
            ).count()
            
            fill_rate = (enrollment_count / course.max_students * 100) if course.max_students > 0 else 0
            course_fill_rates.append(fill_rate)
        
        avg_fill_rate = sum(course_fill_rates) / len(course_fill_rates) if course_fill_rates else 0
        
        return {
            'by_course_type': by_course_type,
            'by_status': by_status,
            'avg_course_fill_rate': avg_fill_rate,
            'sampled_courses': len(course_fill_rates)
        }
    
    def _check_data_quality(self):
        """检查数据质量"""
        print("🧹 检查数据质量...")
        
        quality_metrics = {}
        
        # 数据完整性评分
        completeness = self._assess_data_completeness()
        quality_metrics['completeness'] = completeness
        
        # 数据一致性评分
        consistency = self._assess_data_consistency()
        quality_metrics['consistency'] = consistency
        
        # 数据合理性评分
        reasonableness = self._assess_data_reasonableness()
        quality_metrics['reasonableness'] = reasonableness
        
        # 总体质量评分
        overall_score = (completeness['score'] + consistency['score'] + reasonableness['score']) / 3
        quality_metrics['overall_score'] = overall_score
        
        self.report['data_quality'] = quality_metrics
        print(f"✅ 数据质量检查完成，总体评分: {overall_score:.1f}/100")
    
    def _assess_data_completeness(self):
        """评估数据完整性"""
        score = 100
        issues = []
        
        # 检查基础数据
        if self.report['data_statistics']['users']['students'] == 0:
            score -= 30
            issues.append("没有学生数据")
        
        if self.report['data_statistics']['academic']['courses'] == 0:
            score -= 30
            issues.append("没有课程数据")
        
        if self.report['data_statistics']['infrastructure']['classrooms'] == 0:
            score -= 20
            issues.append("没有教室数据")
        
        if self.report['data_statistics']['academic']['schedules'] == 0:
            score -= 20
            issues.append("没有排课数据")
        
        return {
            'score': max(0, score),
            'issues': issues
        }
    
    def _assess_data_consistency(self):
        """评估数据一致性"""
        score = 100
        issues = []
        
        # 检查约束违例
        total_violations = self.report['hard_constraints']['total_violations']
        if total_violations > 0:
            penalty = min(50, total_violations * 5)
            score -= penalty
            issues.append(f"发现 {total_violations} 个硬约束违例")
        
        return {
            'score': max(0, score),
            'issues': issues
        }
    
    def _assess_data_reasonableness(self):
        """评估数据合理性"""
        score = 100
        issues = []
        
        # 检查平均选课数
        avg_enrollments = self.report['data_statistics']['enrollment_analysis']['avg_enrollments_per_student']
        if avg_enrollments and (avg_enrollments < 3 or avg_enrollments > 12):
            score -= 20
            issues.append(f"学生平均选课数不合理: {avg_enrollments:.1f}")
        
        # 检查教室利用率
        if 'classroom_utilization' in self.report['soft_constraints']:
            utilization_rate = self.report['soft_constraints']['classroom_utilization']['overall_rate']
            if utilization_rate < 30 or utilization_rate > 95:
                score -= 15
                issues.append(f"教室利用率不合理: {utilization_rate:.1f}%")
        
        return {
            'score': max(0, score),
            'issues': issues
        }
    
    def _calculate_compliance_rate(self, violations):
        """计算约束遵守率"""
        total_schedules = self.report['data_statistics']['academic']['active_schedules']
        if total_schedules == 0:
            return 100.0
        
        total_violations = sum(
            len(v) if isinstance(v, list) else 
            sum(v.values()) if isinstance(v, dict) else v 
            for v in violations.values()
        )
        compliance_rate = (1 - total_violations / total_schedules) * 100
        return max(0, compliance_rate)
    
    def _generate_recommendations(self):
        """生成改进建议"""
        print("💡 生成改进建议...")
        
        recommendations = []
        
        # 基于硬约束违例的建议
        violations = self.report['hard_constraints']['violations']
        
        if violations['teacher_time_conflicts']:
            recommendations.append({
                'type': 'critical',
                'title': '解决教师时间冲突',
                'description': f"发现 {len(violations['teacher_time_conflicts'])} 个教师时间冲突，需要重新安排排课",
                'priority': 'high'
            })
        
        if violations['classroom_time_conflicts']:
            recommendations.append({
                'type': 'critical',
                'title': '解决教室时间冲突',
                'description': f"发现 {len(violations['classroom_time_conflicts'])} 个教室时间冲突，需要重新分配教室",
                'priority': 'high'
            })
        
        if violations['capacity_violations']:
            recommendations.append({
                'type': 'warning',
                'title': '调整课程容量',
                'description': f"发现 {len(violations['capacity_violations'])} 个教室容量不足的情况，建议限制选课人数或更换更大的教室",
                'priority': 'medium'
            })
        
        # 基于软约束的建议
        if 'classroom_utilization' in self.report['soft_constraints']:
            utilization = self.report['soft_constraints']['classroom_utilization']['overall_rate']
            if utilization < 50:
                recommendations.append({
                    'type': 'optimization',
                    'title': '提高教室利用率',
                    'description': f"当前教室利用率仅为 {utilization:.1f}%，建议优化排课安排",
                    'priority': 'low'
                })
        
        # 基于数据质量的建议
        quality_score = self.report['data_quality']['overall_score']
        if quality_score < 80:
            recommendations.append({
                'type': 'improvement',
                'title': '提升数据质量',
                'description': f"数据质量评分为 {quality_score:.1f}/100，建议检查和清理数据",
                'priority': 'medium'
            })
        
        self.report['recommendations'] = recommendations
        print(f"✅ 生成了 {len(recommendations)} 条改进建议")
    
    def _output_report(self):
        """输出验证报告"""
        print("\n" + "=" * 60)
        print("📋 数据验证报告")
        print("=" * 60)
        
        # 数据统计摘要
        stats = self.report['data_statistics']
        print(f"📊 数据规模统计：")
        print(f"   学生: {stats['users']['students']:,} 名")
        print(f"   教师: {stats['users']['teachers']:,} 名")
        print(f"   课程: {stats['academic']['courses']:,} 门")
        print(f"   教室: {stats['infrastructure']['classrooms']:,} 间")
        print(f"   排课: {stats['academic']['schedules']:,} 条")
        print(f"   选课: {stats['academic']['enrollments']:,} 条")
        
        # 硬约束验证结果
        print(f"\n🔒 硬约束验证结果：")
        print(f"   违例总数: {self.report['hard_constraints']['total_violations']}")
        print(f"   遵守率: {self.report['hard_constraints']['compliance_rate']:.1f}%")
        
        # 数据质量评估
        print(f"\n🧹 数据质量评估：")
        print(f"   总体评分: {self.report['data_quality']['overall_score']:.1f}/100")
        print(f"   完整性: {self.report['data_quality']['completeness']['score']:.1f}/100")
        print(f"   一致性: {self.report['data_quality']['consistency']['score']:.1f}/100")
        print(f"   合理性: {self.report['data_quality']['reasonableness']['score']:.1f}/100")
        
        # 关键指标
        if 'classroom_utilization' in self.report['soft_constraints']:
            print(f"\n📈 关键指标：")
            utilization = self.report['soft_constraints']['classroom_utilization']['overall_rate']
            print(f"   教室利用率: {utilization:.1f}%")
            
            if 'enrollment_distribution' in self.report['soft_constraints']:
                fill_rate = self.report['soft_constraints']['enrollment_distribution']['avg_course_fill_rate']
                print(f"   课程平均填充率: {fill_rate:.1f}%")
        
        # 改进建议
        if self.report['recommendations']:
            print(f"\n💡 改进建议：")
            for i, rec in enumerate(self.report['recommendations'], 1):
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                print(f"   {i}. {priority_icon} {rec['title']}")
                print(f"      {rec['description']}")
        
        # 保存详细报告
        report_filename = f"data_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 详细报告已保存至: {report_filename}")
        print("=" * 60)