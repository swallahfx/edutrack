"""
Models for the courses app.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.text import slugify


class Course(models.Model):
    """
    Model for courses.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='taught_courses'
    )
    students = models.ManyToManyField(
        User, 
        through='Enrollment',
        related_name='enrolled_courses',
        blank=True,
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Generate and save the slug when creating a course."""
        if not self.slug:
            self.slug = slugify(self.title)
            
            # If the slug already exists, append a number
            original_slug = self.slug
            counter = 1
            while Course.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)
    
    @property
    def enrollment_count(self):
        """Get the number of students enrolled in the course."""
        return self.students.count()
    
    @classmethod
    def get_courses_for_user(cls, user):
        """
        Get courses available to a specific user.
        For teachers: courses they created
        For students: all active courses
        """
        if user.profile.is_teacher:
            return cls.objects.filter(teacher=user)
        else:
            # For students, show all active courses
            return cls.objects.filter(is_active=True)
    
    @classmethod
    def get_enrolled_courses(cls, user):
        """Get courses that a student is enrolled in."""
        if user.profile.is_student:
            return cls.objects.filter(students=user, is_active=True)
        return cls.objects.none()


class Enrollment(models.Model):
    """
    Model for course enrollments.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['course', 'student']
        indexes = [
            models.Index(fields=['course', 'student']),
            models.Index(fields=['student', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"