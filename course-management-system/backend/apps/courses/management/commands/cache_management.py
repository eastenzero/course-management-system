"""
缓存管理命令
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache, caches
from django.db.models import Count, Avg
from apps.courses.models import Course, Enrollment, Grade
from apps.courses.cache_service import course_cache, grade_cache, schedule_cache
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '缓存管理命令：清理、预热、统计缓存'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['clear', 'warmup', 'stats', 'clear-expired'],
            default='stats',
            help='执行的操作：clear(清理), warmup(预热), stats(统计), clear-expired(清理过期)'
        )
        
        parser.add_argument(
            '--cache-type',
            type=str,
            choices=['all', 'course', 'grade', 'schedule'],
            default='all',
            help='缓存类型'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行操作'
        )

    def handle(self, *args, **options):
        action = options['action']
        cache_type = options['cache_type']
        force = options['force']

        self.stdout.write(f"执行缓存操作: {action}, 类型: {cache_type}")

        if action == 'clear':
            self.clear_cache(cache_type, force)
        elif action == 'warmup':
            self.warmup_cache(cache_type)
        elif action == 'stats':
            self.show_cache_stats(cache_type)
        elif action == 'clear-expired':
            self.clear_expired_cache(cache_type)

    def clear_cache(self, cache_type: str, force: bool = False):
        """清理缓存"""
        if not force:
            confirm = input("确定要清理缓存吗？这将删除所有缓存数据。(y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write("操作已取消")
                return

        try:
            if cache_type == 'all':
                # 清理所有缓存
                for cache_alias in ['default', 'api_cache', 'sessions']:
                    cache_instance = caches[cache_alias]
                    cache_instance.clear()
                self.stdout.write(self.style.SUCCESS("已清理所有缓存"))
            
            elif cache_type == 'course':
                course_cache.clear()
                self.stdout.write(self.style.SUCCESS("已清理课程缓存"))
            
            elif cache_type == 'grade':
                grade_cache.clear()
                self.stdout.write(self.style.SUCCESS("已清理成绩缓存"))
            
            elif cache_type == 'schedule':
                schedule_cache.clear()
                self.stdout.write(self.style.SUCCESS("已清理课程表缓存"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"清理缓存失败: {e}"))

    def warmup_cache(self, cache_type: str):
        """预热缓存"""
        self.stdout.write("开始预热缓存...")

        try:
            if cache_type in ['all', 'course']:
                self._warmup_course_cache()
            
            if cache_type in ['all', 'grade']:
                self._warmup_grade_cache()
            
            if cache_type in ['all', 'schedule']:
                self._warmup_schedule_cache()

            self.stdout.write(self.style.SUCCESS("缓存预热完成"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"缓存预热失败: {e}"))

    def _warmup_course_cache(self):
        """预热课程缓存"""
        self.stdout.write("预热课程缓存...")
        
        # 预热活跃课程列表
        active_courses = Course.objects.filter(is_active=True).select_related().prefetch_related('teachers')
        
        # 为不同用户类型预热课程列表
        for user_type in ['student', 'teacher', 'admin']:
            cache_key = f"course_list:warmup:{user_type}"
            course_cache.set(cache_key, list(active_courses), 600)
        
        # 预热热门课程详情
        popular_courses = Course.objects.annotate(
            enrollment_count=Count('enrollments')
        ).filter(is_active=True).order_by('-enrollment_count')[:20]
        
        for course in popular_courses:
            cache_key = course_cache.get_course_detail_key(course.id)
            course_cache.set(cache_key, course, 600)
        
        self.stdout.write(f"已预热 {len(popular_courses)} 个热门课程")

    def _warmup_grade_cache(self):
        """预热成绩缓存"""
        self.stdout.write("预热成绩缓存...")
        
        # 预热活跃学生的成绩统计
        active_students = User.objects.filter(
            user_type='student',
            is_active=True,
            enrollments__is_active=True
        ).distinct()[:50]  # 限制数量避免过度预热
        
        for student in active_students:
            cache_key = grade_cache.get_grade_statistics_key(student.id)
            # 这里可以调用实际的统计方法
            # stats = calculate_student_statistics(student.id)
            # grade_cache.set(cache_key, stats, 600)
        
        self.stdout.write(f"已预热 {len(active_students)} 个学生的成绩统计")

    def _warmup_schedule_cache(self):
        """预热课程表缓存"""
        self.stdout.write("预热课程表缓存...")
        
        # 预热当前周的课程表
        current_week = 1  # 这里应该获取当前周数
        
        active_users = User.objects.filter(
            is_active=True,
            user_type__in=['student', 'teacher']
        )[:100]  # 限制数量
        
        for user in active_users:
            cache_key = schedule_cache.get_schedule_key(user.id, current_week)
            # 这里可以调用实际的课程表查询方法
            # schedule_data = get_user_schedule(user.id, current_week)
            # schedule_cache.set(cache_key, schedule_data, 600)
        
        self.stdout.write(f"已预热 {len(active_users)} 个用户的课程表")

    def show_cache_stats(self, cache_type: str):
        """显示缓存统计"""
        self.stdout.write("缓存统计信息:")
        
        try:
            if cache_type in ['all', 'course']:
                self._show_cache_alias_stats('api_cache', '课程API缓存')
            
            if cache_type in ['all']:
                self._show_cache_alias_stats('default', '默认缓存')
                self._show_cache_alias_stats('sessions', '会话缓存')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"获取缓存统计失败: {e}"))

    def _show_cache_alias_stats(self, alias: str, name: str):
        """显示特定缓存别名的统计"""
        try:
            cache_instance = caches[alias]
            
            # 尝试获取Redis统计信息
            if hasattr(cache_instance, '_cache') and hasattr(cache_instance._cache, 'get_client'):
                client = cache_instance._cache.get_client()
                info = client.info()
                
                self.stdout.write(f"\n{name} ({alias}):")
                self.stdout.write(f"  连接的客户端数: {info.get('connected_clients', 'N/A')}")
                self.stdout.write(f"  使用的内存: {info.get('used_memory_human', 'N/A')}")
                self.stdout.write(f"  键的数量: {info.get('db1', {}).get('keys', 'N/A')}")
                self.stdout.write(f"  命中次数: {info.get('keyspace_hits', 'N/A')}")
                self.stdout.write(f"  未命中次数: {info.get('keyspace_misses', 'N/A')}")
                
                hits = info.get('keyspace_hits', 0)
                misses = info.get('keyspace_misses', 0)
                if hits + misses > 0:
                    hit_rate = hits / (hits + misses) * 100
                    self.stdout.write(f"  命中率: {hit_rate:.2f}%")
            else:
                self.stdout.write(f"\n{name} ({alias}): 无法获取详细统计信息")
                
        except Exception as e:
            self.stdout.write(f"\n{name} ({alias}): 获取统计失败 - {e}")

    def clear_expired_cache(self, cache_type: str):
        """清理过期缓存"""
        self.stdout.write("清理过期缓存...")
        
        try:
            # Redis会自动清理过期键，这里主要是触发清理操作
            if cache_type in ['all', 'course']:
                course_cache.delete_pattern('course_list:*:expired')
            
            if cache_type in ['all', 'grade']:
                grade_cache.delete_pattern('grade_stats:*:expired')
            
            if cache_type in ['all', 'schedule']:
                schedule_cache.delete_pattern('schedule:*:expired')
            
            self.stdout.write(self.style.SUCCESS("过期缓存清理完成"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"清理过期缓存失败: {e}"))
