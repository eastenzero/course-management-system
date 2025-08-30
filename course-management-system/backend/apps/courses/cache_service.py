"""
缓存服务模块
"""

from django.core.cache import cache, caches
from django.conf import settings
from typing import Any, Optional, List, Dict
import json
import hashlib
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """缓存服务类"""
    
    def __init__(self, cache_alias: str = 'default'):
        self.cache = caches[cache_alias]
        self.default_timeout = getattr(settings, 'CACHE_TIMEOUT', 300)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        try:
            return self.cache.get(key, default)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            timeout = timeout or self.default_timeout
            return self.cache.set(key, value, timeout)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return self.cache.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存"""
        try:
            return self.cache.delete_pattern(pattern)
        except Exception as e:
            logger.error(f"Cache delete pattern error for pattern {pattern}: {e}")
            return 0
    
    def get_or_set(self, key: str, callable_func, timeout: Optional[int] = None) -> Any:
        """获取缓存，如果不存在则设置"""
        try:
            value = self.get(key)
            if value is None:
                value = callable_func()
                self.set(key, value, timeout)
            return value
        except Exception as e:
            logger.error(f"Cache get_or_set error for key {key}: {e}")
            return callable_func()
    
    def increment(self, key: str, delta: int = 1) -> int:
        """增加计数器"""
        try:
            return self.cache.incr(key, delta)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            self.cache.clear()
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False


class CourseCache(CacheService):
    """课程相关缓存"""
    
    def __init__(self):
        super().__init__('api_cache')
    
    def get_course_list_key(self, user_id: int, filters: Dict = None) -> str:
        """生成课程列表缓存键"""
        filter_str = json.dumps(filters or {}, sort_keys=True)
        filter_hash = hashlib.md5(filter_str.encode()).hexdigest()[:8]
        return f"course_list:{user_id}:{filter_hash}"
    
    def get_course_detail_key(self, course_id: int) -> str:
        """生成课程详情缓存键"""
        return f"course_detail:{course_id}"
    
    def get_course_statistics_key(self, course_id: int) -> str:
        """生成课程统计缓存键"""
        return f"course_stats:{course_id}"
    
    def get_enrollment_key(self, user_id: int) -> str:
        """生成用户选课缓存键"""
        return f"user_enrollments:{user_id}"
    
    def invalidate_course_cache(self, course_id: int):
        """清除课程相关缓存"""
        patterns = [
            f"course_detail:{course_id}",
            f"course_stats:{course_id}",
            f"course_list:*",
            f"user_enrollments:*"
        ]
        for pattern in patterns:
            self.delete_pattern(pattern)
    
    def invalidate_user_cache(self, user_id: int):
        """清除用户相关缓存"""
        patterns = [
            f"user_enrollments:{user_id}",
            f"course_list:{user_id}:*",
            f"student_dashboard:{user_id}",
            f"teacher_dashboard:{user_id}"
        ]
        for pattern in patterns:
            self.delete_pattern(pattern)


class GradeCache(CacheService):
    """成绩相关缓存"""
    
    def __init__(self):
        super().__init__('api_cache')
    
    def get_grade_list_key(self, user_id: int, course_id: Optional[int] = None) -> str:
        """生成成绩列表缓存键"""
        if course_id:
            return f"grades:{user_id}:course:{course_id}"
        return f"grades:{user_id}:all"
    
    def get_grade_statistics_key(self, user_id: int) -> str:
        """生成成绩统计缓存键"""
        return f"grade_stats:{user_id}"
    
    def get_course_grade_distribution_key(self, course_id: int) -> str:
        """生成课程成绩分布缓存键"""
        return f"grade_distribution:{course_id}"
    
    def get_class_comparison_key(self, class_name: str, semester: str) -> str:
        """生成班级对比缓存键"""
        return f"class_comparison:{class_name}:{semester}"
    
    def invalidate_grade_cache(self, user_id: int, course_id: Optional[int] = None):
        """清除成绩相关缓存"""
        patterns = [
            f"grades:{user_id}:*",
            f"grade_stats:{user_id}",
            f"student_dashboard:{user_id}"
        ]
        if course_id:
            patterns.extend([
                f"grade_distribution:{course_id}",
                f"course_stats:{course_id}"
            ])
        
        for pattern in patterns:
            self.delete_pattern(pattern)


class ScheduleCache(CacheService):
    """课程表相关缓存"""
    
    def __init__(self):
        super().__init__('api_cache')
    
    def get_schedule_key(self, user_id: int, week: Optional[int] = None) -> str:
        """生成课程表缓存键"""
        if week:
            return f"schedule:{user_id}:week:{week}"
        return f"schedule:{user_id}:current"
    
    def get_classroom_schedule_key(self, classroom_id: int, date: str) -> str:
        """生成教室课程表缓存键"""
        return f"classroom_schedule:{classroom_id}:{date}"
    
    def get_teacher_schedule_key(self, teacher_id: int, semester: str) -> str:
        """生成教师课程表缓存键"""
        return f"teacher_schedule:{teacher_id}:{semester}"
    
    def invalidate_schedule_cache(self, user_id: Optional[int] = None, course_id: Optional[int] = None):
        """清除课程表相关缓存"""
        patterns = []
        
        if user_id:
            patterns.extend([
                f"schedule:{user_id}:*",
                f"student_dashboard:{user_id}",
                f"teacher_dashboard:{user_id}"
            ])
        
        if course_id:
            patterns.extend([
                f"schedule:*",
                f"classroom_schedule:*",
                f"teacher_schedule:*"
            ])
        
        for pattern in patterns:
            self.delete_pattern(pattern)


def cache_result(timeout: int = 300, cache_alias: str = 'api_cache'):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__module__}.{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cache_service = CacheService(cache_alias)
            result = cache_service.get(cache_key)
            
            if result is not None:
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_cache_on_save(cache_patterns: List[str]):
    """模型保存时清除缓存的装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            
            # 清除相关缓存
            cache_service = CacheService()
            for pattern in cache_patterns:
                # 替换模式中的占位符
                formatted_pattern = pattern.format(
                    id=getattr(self, 'id', ''),
                    user_id=getattr(self, 'user_id', ''),
                    course_id=getattr(self, 'course_id', ''),
                    student_id=getattr(self, 'student_id', '')
                )
                cache_service.delete_pattern(formatted_pattern)
            
            return result
        return wrapper
    return decorator


# 缓存实例
course_cache = CourseCache()
grade_cache = GradeCache()
schedule_cache = ScheduleCache()
default_cache = CacheService()
