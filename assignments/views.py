"""
Views for the assignments app.
"""

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, mixins, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Assignment, Submission
from .permissions import (
    IsAssignmentTeacher,
    IsEnrolledStudentOrTeacher,
    CanSubmitAssignment,
    IsSubmissionOwnerOrTeacher,
    CanReviewSubmission,
)
from .serializers import (
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    AssignmentCreateUpdateSerializer,
    SubmissionListSerializer,
    SubmissionDetailSerializer,
    SubmissionCreateSerializer,
    SubmissionReviewSerializer,
)
from courses.models import Course
from users.permissions import IsTeacher, IsStudent


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for assignments.
    """
    queryset = Assignment.objects.annotate(submission_count=Count('submissions'))
    serializer_class = AssignmentListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'due_date', 'submission_count']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Set permissions based on action:
        - create/update/delete: must be the course teacher
        - list/retrieve: must be enrolled or the teacher
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAssignmentTeacher]
        elif self.action == 'submit':
            permission_classes = [IsAuthenticated, CanSubmitAssignment]
        else:
            permission_classes = [IsAuthenticated, IsEnrolledStudentOrTeacher]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return the appropriate serializer based on the action."""
        if self.action == 'retrieve':
            return AssignmentDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AssignmentCreateUpdateSerializer
        return AssignmentListSerializer
    
    def get_queryset(self):
        """Filter assignments based on user role and query parameters."""
        user = self.request.user
        
        if not user.is_authenticated:
            return Assignment.objects.none()
        
        # Get course_id from query parameters
        course_id = self.request.query_params.get('course')
        
        # Base queryset with annotation
        queryset = Assignment.objects.annotate(submission_count=Count('submissions'))
        
        # Filter by course if specified
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter based on user role
        if user.profile.is_teacher:
            # Teachers see assignments for courses they teach
            return queryset.filter(course__teacher=user)
        else:
            # Students see assignments for courses they're enrolled in
            return queryset.filter(
                course__students=user,
                course__is_active=True,
                is_active=True
            )
    
    @action(detail=True, methods=['post'], serializer_class=SubmissionCreateSerializer)
    def submit(self, request, pk=None):
        """Submit an assignment."""
        assignment = self.get_object()
        
        # Check if student has already submitted
        if Submission.objects.filter(assignment=assignment, student=request.user).exists():
            return Response(
                {'detail': 'You have already submitted this assignment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data={
            'assignment': assignment.id,
            'content': request.data.get('content', ''),
            'file': request.data.get('file')
        })
        
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for submissions.
    """
    serializer_class = SubmissionListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['assignment', 'status']
    ordering_fields = ['submitted_at', 'reviewed_at']
    ordering = ['-submitted_at']
    http_method_names = ['get', 'post', 'patch', 'head', 'options']  # No PUT or DELETE
    
    def get_queryset(self):
        """Filter submissions based on user role."""
        user = self.request.user
        
        if not user.is_authenticated:
            return Submission.objects.none()
        
        if user.profile.is_teacher:
            # Teachers see submissions for assignments in their courses
            return Submission.objects.filter(assignment__course__teacher=user)
        else:
            # Students see their own submissions
            return Submission.objects.filter(student=user)
    
    def get_permissions(self):
        """
        Set permissions based on action:
        - retrieve: must be the submission owner or the teacher
        - review: must be the teacher
        """
        if self.action == 'review':
            permission_classes = [IsAuthenticated, CanReviewSubmission]
        else:
            permission_classes = [IsAuthenticated, IsSubmissionOwnerOrTeacher]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return the appropriate serializer based on the action."""
        if self.action == 'retrieve':
            return SubmissionDetailSerializer
        elif self.action == 'review':
            return SubmissionReviewSerializer
        elif self.action == 'create':
            return SubmissionCreateSerializer
        return SubmissionListSerializer
    
    @action(detail=True, methods=['patch'], serializer_class=SubmissionReviewSerializer)
    def review(self, request, pk=None):
        """Review a submission."""
        submission = self.get_object()
        serializer = self.get_serializer(submission, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save(
                status=Submission.REVIEWED,
                reviewed_at=timezone.now()
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)