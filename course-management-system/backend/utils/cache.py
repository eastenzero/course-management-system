"""
缓存工具模块
提供Redis缓存的封装和常用缓存操作
"""

from django.core.cache import cache
from django.conf import settings
import json
import hashlib
from functools import wraps
from typing import Any, Optional, Callable


class CacheManager:
    """缓存管理器"""
    
    # 缓存键前缀
    COURSE_PREFIX = 'course:'
    USER_PREFIX = 'user:'
    SCHEDULE_PREFIX = 'schedule:'
    CLASSROOM_PREFIX = 'classroom:'
    STATISTICS_PREFIX = 'stats:'
    
    # 缓存时间（秒）
    SHORT_CACHE_TIME = 60 * 5      # 5分钟
    MEDIUM_CACHE_TIME = 60 * 30    # 30分钟
    LONG_CACHE_TIME = 60 * 60 * 2  # 2小时
    
    @classmethod
    def get_cache_key(cls, prefix: str, *args) -> str:
        """生成缓存键"""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ':'.join(key_parts)
    
    @classmethod
    def get_hash_key(cls, prefix: str, data: dict) -> str:
        """根据数据生成哈希缓存键"""
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    @classmethod
    def set_cache(cls, key: str, value: Any, timeout: int = MEDIUM_CACHE_TIME) -> bool:
        """设置缓存"""
        try:
            return cache.set(key, value, timeout)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @classmethod
    def get_cache(cls, key: str, default: Any = None) -> Any:
        """获取缓存"""
        try:
            return cache.get(key, default)
        except Exception as e:
            print(f"Cache get error: {e}")
            return default
    
    @classmethod
    def delete_cache(cls, key: str) -> bool:
        """删除缓存"""
        try:
            return cache.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    @classmethod
    def delete_pattern(cls, pattern: str) -> int:
        """删除匹配模式的缓存键"""
        try:
            if hasattr(cache, 'delete_pattern'):
                return cache.delete_pattern(pattern)
            else:
                # 如果不支持模式删除，返回0
                return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0
    
    @classmethod
    def clear_user_cache(cls, user_id: int):
        """清除用户相关缓存"""
        patterns = [
            f"{cls.USER_PREFIX}{user_id}:*",
            f"{cls.SCHEDULE_PREFIX}user:{user_id}:*",
        ]
        for pattern in patterns:
            cls.delete_pattern(pattern)
    
    @classmethod
    def clear_course_cache(cls, course_id: int):
        """清除课程相关缓存"""
        patterns = [
            f"{cls.COURSE_PREFIX}{course_id}:*",
            f"{cls.SCHEDULE_PREFIX}course:{course_id}:*",
            f"{cls.STATISTICS_PREFIX}course:*",
        ]
        for pattern in patterns:
            cls.delete_pattern(pattern)
    
    @classmethod
    def clear_schedule_cache(cls, semester: str = None):
        """清除排课相关缓存"""
        if semester:
            pattern = f"{cls.SCHEDULE_PREFIX}*{semester}*"
        else:
            pattern = f"{cls.SCHEDULE_PREFIX}*"
        cls.delete_pattern(pattern)


def cache_result(timeout: int = CacheManager.MEDIUM_CACHE_TIME, 
                key_prefix: str = '', 
                key_func: Optional[Callable] = None):
    """
    缓存装饰器
    
    Args:
        timeout: 缓存时间（秒）
        key_prefix: 缓存键前缀
        key_func: 自定义键生成函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认键生成逻辑
                key_parts = [key_prefix or func.__name__]
                key_parts.extend([str(arg) for arg in args])
                key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
                cache_key = ':'.join(key_parts)
            
            # 尝试从缓存获取
            result = CacheManager.get_cache(cache_key)
            if result is not None:
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            CacheManager.set_cache(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def invalidate_cache_on_save(cache_patterns: list):
    """
    模型保存时清除缓存的装饰器
    
    Args:
        cache_patterns: 要清除的缓存模式列表
    """
    def decorator(save_method):
        @wraps(save_method)
        def wrapper(self, *args, **kwargs):
            result = save_method(self, *args, **kwargs)
            
            # 清除相关缓存
            for pattern in cache_patterns:
                # 替换模式中的占位符
                if hasattr(self, 'id'):
                    pattern = pattern.replace('{id}', str(self.id))
                if hasattr(self, 'semester'):
                    pattern = pattern.replace('{semester}', str(self.semester))
                
                CacheManager.delete_pattern(pattern)
            
            return result
        return wrapper
    return decorator


# 常用缓存操作函数

def get_course_list_cache(filters: dict) -> Optional[list]:
    """获取课程列表缓存"""
    cache_key = CacheManager.get_hash_key(CacheManager.COURSE_PREFIX + 'list', filters)
    return CacheManager.get_cache(cache_key)


def set_course_list_cache(filters: dict, data: list, timeout: int = CacheManager.SHORT_CACHE_TIME):
    """设置课程列表缓存"""
    cache_key = CacheManager.get_hash_key(CacheManager.COURSE_PREFIX + 'list', filters)
    CacheManager.set_cache(cache_key, data, timeout)


def get_schedule_table_cache(semester: str, user_type: str, user_id: int) -> Optional[dict]:
    """获取课程表缓存"""
    cache_key = CacheManager.get_cache_key(
        CacheManager.SCHEDULE_PREFIX + 'table',
        semester, user_type, user_id
    )
    return CacheManager.get_cache(cache_key)


def set_schedule_table_cache(semester: str, user_type: str, user_id: int, data: dict):
    """设置课程表缓存"""
    cache_key = CacheManager.get_cache_key(
        CacheManager.SCHEDULE_PREFIX + 'table',
        semester, user_type, user_id
    )
    CacheManager.set_cache(cache_key, data, CacheManager.SHORT_CACHE_TIME)


def get_statistics_cache(stat_type: str, filters: dict) -> Optional[dict]:
    """获取统计数据缓存"""
    cache_key = CacheManager.get_hash_key(
        CacheManager.STATISTICS_PREFIX + stat_type, 
        filters
    )
    return CacheManager.get_cache(cache_key)


def set_statistics_cache(stat_type: str, filters: dict, data: dict):
    """设置统计数据缓存"""
    cache_key = CacheManager.get_hash_key(
        CacheManager.STATISTICS_PREFIX + stat_type, 
        filters
    )
    CacheManager.set_cache(cache_key, data, CacheManager.LONG_CACHE_TIME)
