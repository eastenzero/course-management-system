from rest_framework import permissions


class IsStudentOwner(permissions.BasePermission):
    """
    只允许学生访问自己的数据
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'student'
        )
    
    def has_object_permission(self, request, view, obj):
        # 检查对象是否属于当前学生
        if hasattr(obj, 'student'):
            return obj.student == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class CanEnrollCourse(permissions.BasePermission):
    """
    检查学生是否可以选课
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'student'
        )


class CanDropCourse(permissions.BasePermission):
    """
    检查学生是否可以退课
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'student'
        )
