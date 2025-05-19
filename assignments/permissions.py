"""
Custom permissions for the assignments app.
"""

from rest_framework import permissions


class IsAssignmentTeacher(permissions.BasePermission):
    """
    Allow access only to the teacher who created the course that the assignment belongs to.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.is_teacher
    
    def has_object_permission(self, request, view, obj):
        return obj.course.teacher == request.user


class IsEnrolledStudentOrTeacher(permissions.BasePermission):
    """
    Allow access only to the teacher who created the course
    or students enrolled in the course.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Teacher who created the course
        if obj.course.teacher == request.user:
            return True
        
        # Student enrolled in the course
        return (
            request.user.profile.is_student and 
            obj.course.students.filter(id=request.user.id).exists()
        )


class CanSubmitAssignment(permissions.BasePermission):
    """
    Allow only enrolled students to submit assignments.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.is_student
    
    def has_object_permission(self, request, view, obj):
        # Student must be enrolled in the course
        return obj.course.students.filter(id=request.user.id).exists()


class IsSubmissionOwnerOrTeacher(permissions.BasePermission):
    """
    Allow access only to the student who submitted or the teacher.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Teacher of the course
        if obj.assignment.course.teacher == request.user:
            return True
        
        # Student who submitted
        return obj.student == request.user


class CanReviewSubmission(permissions.BasePermission):
    """
    Allow only the teacher of the course to review submissions.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.is_teacher
    
    def has_object_permission(self, request, view, obj):
        return obj.assignment.course.teacher == request.user