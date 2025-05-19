"""
Serializers for the courses app.
"""

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Course, Enrollment


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for listing courses."""
    
    teacher_name = serializers.SerializerMethodField()
    enrollment_count = serializers.IntegerField(read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'teacher', 'teacher_name',
            'enrollment_count', 'is_enrolled', 'slug', 'created_at',
            'is_active', 'thumbnail'
        ]
        read_only_fields = ['id', 'slug', 'teacher_name', 'created_at', 'enrollment_count']
    
    def get_teacher_name(self, obj):
        """Get the teacher's full name."""
        return f"{obj.teacher.first_name} {obj.teacher.last_name}".strip() or obj.teacher.username
    
    def get_is_enrolled(self, obj):
        """Check if the current user is enrolled in the course."""
        user = self.context['request'].user
        if not user.is_authenticated or user.profile.is_teacher:
            return False
        return obj.students.filter(id=user.id).exists()


class CourseDetailSerializer(CourseListSerializer):
    """Serializer for course details."""
    
    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ['students']
        read_only_fields = CourseListSerializer.Meta.read_only_fields + ['students']


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating courses."""
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'is_active', 'thumbnail']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """Assign the current user as the teacher when creating a course."""
        user = self.context['request'].user
        validated_data['teacher'] = user
        return super().create(validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for enrollments."""
    
    student_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'student', 'student_name', 'enrolled_at', 'is_active']
        read_only_fields = ['id', 'student', 'student_name', 'enrolled_at']
    
    def get_student_name(self, obj):
        """Get the student's full name."""
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username
    
    def create(self, validated_data):
        """Assign the current user as the student when enrolling."""
        user = self.context['request'].user
        validated_data['student'] = user
        return super().create(validated_data)


class UserBriefSerializer(serializers.ModelSerializer):
    """Brief serializer for user data in courses."""
    
    role = serializers.CharField(source='profile.role', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role']