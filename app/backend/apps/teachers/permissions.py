from rest_framework import permissions


class IsTeacherOwner(permissions.BasePermission):
    """
    只允许教师访问自己的数据
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'teacher'
        )
    
    def has_object_permission(self, request, view, obj):
        # 检查对象是否属于当前教师
        if hasattr(obj, 'teacher'):
            return obj.teacher == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'teachers'):
            return request.user in obj.teachers.all()
        return False


class CanManageCourse(permissions.BasePermission):
    """
    检查教师是否可以管理指定课程
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'teacher'
        )
    
    def has_object_permission(self, request, view, obj):
        # 检查教师是否教授该课程
        if hasattr(obj, 'course'):
            return request.user in obj.course.teachers.all()
        elif hasattr(obj, 'teachers'):
            return request.user in obj.teachers.all()
        return False


class CanGradeStudents(permissions.BasePermission):
    """
    检查教师是否可以给学生打分
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'teacher'
        )
    
    def has_object_permission(self, request, view, obj):
        # 检查教师是否教授该课程
        if hasattr(obj, 'course'):
            return request.user in obj.course.teachers.all()
        return False
