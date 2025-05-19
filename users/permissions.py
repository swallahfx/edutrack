"""
Custom permissions for the users app.
"""

from rest_framework import permissions


class IsOwnProfile(permissions.BasePermission):
    """
    Allow users to edit only their own profile.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Instance must be the user's own profile
        return obj == request.user


class IsTeacher(permissions.BasePermission):
    """
    Allow access only to users with the teacher role.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.is_teacher


class IsStudent(permissions.BasePermission):
    """
    Allow access only to users with the student role.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.is_student