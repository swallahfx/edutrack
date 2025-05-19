"""
Views for the courses app.
"""

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Course, Enrollment
from .permissions import IsCourseTeacher, IsEnrolledOrTeacher, CanEnrollInCourse
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    CourseCreateUpdateSerializer,
    EnrollmentSerializer,
    UserBriefSerializer,
)
from users.permissions import IsTeacher, IsStudent


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for courses.
    """
    queryset = Course.objects.annotate(enrollment_count=Count('students'))
    serializer_class = CourseListSerializer
    lookup_field = 'slug'
    filterset_fields = ['is_active', 'teacher']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'enrollment_count']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Set permissions based on action:
        - create: must be a teacher
        - update/delete: must be the course teacher
        - list/retrieve: authenticated users
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsTeacher]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsCourseTeacher]
        elif self.action in ['enroll', 'unenroll']:
            permission_classes = [IsAuthenticated, CanEnrollInCourse]
        elif self.action in ['students']:
            permission_classes = [IsAuthenticated, IsCourseTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return the appropriate serializer based on the action."""
        if self.action == 'retrieve':
            return CourseDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseListSerializer
    
    def get_queryset(self):
        """Filter courses based on user role."""
        user = self.request.user
        
        if not user.is_authenticated:
            return Course.objects.none()
        
        # For list view, filter by role
        if self.action == 'list':
            if user.profile.is_teacher:
                # Teachers see their own courses
                return Course.objects.filter(teacher=user).annotate(enrollment_count=Count('students'))
            else:
                # Students see all active courses
                return Course.objects.filter(is_active=True).annotate(enrollment_count=Count('students'))
        
        # For other actions, maintain the complete queryset
        return self.queryset
    
    @method_decorator(cache_page(60*5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        """List courses with caching."""
        return super().list(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, slug=None):
        """Enroll the current student in a course."""
        course = self.get_object()
        
        # Check if student is already enrolled
        if Enrollment.objects.filter(course=course, student=request.user).exists():
            return Response(
                {'detail': 'You are already enrolled in this course.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create enrollment
        enrollment = Enrollment.objects.create(course=course, student=request.user)
        serializer = EnrollmentSerializer(enrollment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def unenroll(self, request, slug=None):
        """Unenroll the current student from a course."""
        course = self.get_object()
        
        # Get and delete enrollment
        enrollment = get_object_or_404(Enrollment, course=course, student=request.user)
        enrollment.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def students(self, request, slug=None):
        """Get list of students enrolled in a course."""
        course = self.get_object()
        students = course.students.all()
        serializer = UserBriefSerializer(students, many=True)
        return Response(serializer.data)


class EnrollmentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint for enrollments.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter enrollments based on user role."""
        user = self.request.user
        
        if user.profile.is_teacher:
            # Teachers see enrollments for their courses
            return Enrollment.objects.filter(course__teacher=user)
        else:
            # Students see their own enrollments
            return Enrollment.objects.filter(student=user)