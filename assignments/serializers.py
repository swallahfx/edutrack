"""
Serializers for the assignments app.
"""

from django.utils import timezone
from rest_framework import serializers

from .models import Assignment, Submission
from courses.models import Course


class AssignmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing assignments."""
    
    course_title = serializers.StringRelatedField(source='course.title', read_only=True)
    submission_count = serializers.IntegerField(read_only=True)
    has_submitted = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'course', 'course_title',
            'due_date', 'points', 'created_at', 'is_active',
            'submission_count', 'has_submitted'
        ]
        read_only_fields = ['id', 'created_at', 'submission_count', 'course_title']
    
    def get_has_submitted(self, obj):
        """Check if the current user has submitted this assignment."""
        user = self.context['request'].user
        if not user.is_authenticated or user.profile.is_teacher:
            return False
        return obj.submissions.filter(student=user).exists()


class AssignmentDetailSerializer(AssignmentListSerializer):
    """Serializer for assignment details."""
    
    class Meta(AssignmentListSerializer.Meta):
        pass


class AssignmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating assignments."""
    
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'course', 'due_date', 'points', 'is_active']
        read_only_fields = ['id']
    
    def validate_course(self, value):
        """Ensure the user is the teacher of the course."""
        if value.teacher != self.context['request'].user:
            raise serializers.ValidationError("You can only create assignments for courses you teach.")
        return value


class SubmissionListSerializer(serializers.ModelSerializer):
    """Serializer for listing submissions."""
    
    student_name = serializers.SerializerMethodField()
    assignment_title = serializers.StringRelatedField(source='assignment.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title', 'student', 'student_name',
            'submitted_at', 'status', 'is_late'
        ]
        read_only_fields = [
            'id', 'student', 'student_name', 'submitted_at', 
            'status', 'assignment_title', 'is_late'
        ]
    
    def get_student_name(self, obj):
        """Get the student's full name."""
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username


class SubmissionDetailSerializer(serializers.ModelSerializer):
    """Serializer for submission details."""
    
    student_name = serializers.SerializerMethodField()
    assignment_title = serializers.StringRelatedField(source='assignment.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title', 'student', 'student_name',
            'content', 'file', 'submitted_at', 'status', 'feedback',
            'reviewed_at', 'is_late'
        ]
        read_only_fields = [
            'id', 'student', 'student_name', 'submitted_at', 
            'status', 'assignment_title', 'reviewed_at', 'is_late'
        ]
    
    def get_student_name(self, obj):
        """Get the student's full name."""
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating submissions."""
    
    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'content', 'file']
        read_only_fields = ['id']
    
    def validate_assignment(self, value):
        """
        Validate that:
        1. The assignment is active
        2. The student is enrolled in the course
        3. The student hasn't already submitted
        """
        user = self.context['request'].user
        
        # Check if assignment is active
        if not value.is_active:
            raise serializers.ValidationError("This assignment is no longer active.")
        
        # Check if student is enrolled in the course
        if not value.course.students.filter(id=user.id).exists():
            raise serializers.ValidationError("You must be enrolled in the course to submit assignments.")
        
        # Check if student has already submitted
        if value.submissions.filter(student=user).exists():
            raise serializers.ValidationError("You have already submitted this assignment.")
        
        return value
    
    def create(self, validated_data):
        """Assign the current user as the student when submitting."""
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class SubmissionReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviewing submissions."""
    
    class Meta:
        model = Submission
        fields = ['id', 'feedback', 'status']
        read_only_fields = ['id']
    
    def validate(self, attrs):
        """Set status to reviewed and add timestamp."""
        attrs['status'] = Submission.REVIEWED
        attrs['reviewed_at'] = timezone.now()
        return attrs