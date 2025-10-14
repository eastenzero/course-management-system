from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    只允许对象的所有者或管理员访问
    """
    
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何已认证用户
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写入权限只允许对象的所有者或管理员
        return obj == request.user or request.user.user_type in ['admin', 'academic_admin']


class IsAdminUser(permissions.BasePermission):
    """
    只允许管理员用户访问
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['admin', 'academic_admin']
        )


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    只允许教师或管理员访问
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['teacher', 'admin', 'academic_admin']
        )


class IsStudentOrTeacherOrAdmin(permissions.BasePermission):
    """
    允许学生、教师或管理员访问
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['student', 'teacher', 'admin', 'academic_admin']
        )


class IsAcademicAdminOrAdmin(permissions.BasePermission):
    """
    只允许教务管理员或超级管理员访问
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['admin', 'academic_admin']
        )


class CanManageCourses(permissions.BasePermission):
    """
    可以管理课程的权限（教务管理员和超级管理员）
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['admin', 'academic_admin']
        )


class CanViewOwnCourses(permissions.BasePermission):
    """
    可以查看自己课程的权限
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # 管理员可以查看所有课程
        if request.user.user_type in ['admin', 'academic_admin']:
            return True
        
        # 教师可以查看自己教授的课程
        if request.user.user_type == 'teacher':
            return obj.teachers.filter(id=request.user.id).exists()
        
        # 学生可以查看自己选修的课程
        if request.user.user_type == 'student':
            # 这里需要根据选课关系来判断，暂时返回True
            return True
        
        return False


class CanManageSchedules(permissions.BasePermission):
    """
    可以管理课程表的权限
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['admin', 'academic_admin']
        )


class CanViewSchedules(permissions.BasePermission):
    """
    可以查看课程表的权限
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsStudent(permissions.BasePermission):
    """
    只允许学生访问
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'student'
        )


class IsTeacher(permissions.BasePermission):
    """
    只允许教师访问
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.user_type == 'teacher'
        )
