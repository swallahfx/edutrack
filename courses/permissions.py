"""
Custom permissions for the courses app.
"""

from rest_framework import permissions


class IsCourseTeacher(permissions.BasePermission):
    """
    Allow access only to the teacher who created the course.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.is_teacher
    
    def has_object_permission(self, request, view, obj):
        return obj.teacher == request.user


class IsEnrolledOrTeacher(permissions.BasePermission):
    """
    Allow access only to the teacher who created the course
    or students enrolled in the course.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Teacher who created the course
        if obj.teacher == request.user:
            return True
        
        # Student enrolled in the course
        return request.user.profile.is_student and obj.students.filter(id=request.user.id).exists()


class CanEnrollInCourse(permissions.BasePermission):
    """
    Allow students to enroll in courses.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.is_student