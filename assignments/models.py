"""
Models for the assignments app.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

from courses.models import Course


class Assignment(models.Model):
    """
    Model for course assignments.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    due_date = models.DateTimeField(null=True, blank=True)
    points = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['due_date']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.course.title})"
    
    @property
    def teacher(self):
        """Get the teacher (course creator) for this assignment."""
        return self.course.teacher
    
    @property
    def submission_count(self):
        """Get the number of submissions for this assignment."""
        return self.submissions.count()


class Submission(models.Model):
    """
    Model for assignment submissions.
    """
    PENDING = 'pending'
    REVIEWED = 'reviewed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending Review'),
        (REVIEWED, 'Reviewed'),
    ]
    
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    content = models.TextField()
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES,
        default=PENDING
    )
    feedback = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']
        indexes = [
            models.Index(fields=['assignment', 'student']),
            models.Index(fields=['status']),
            models.Index(fields=['submitted_at']),
        ]
    
    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"
    
    @property
    def course(self):
        """Get the course for this submission."""
        return self.assignment.course
    
    @property
    def teacher(self):
        """Get the teacher (course creator) for this submission."""
        return self.assignment.teacher
    
    @property
    def is_late(self):
        """Check if the submission was submitted after the due date."""
        if not self.assignment.due_date:
            return False
        return self.submitted_at > self.assignment.due_date