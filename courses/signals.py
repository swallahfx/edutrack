"""
Signal handlers for the courses app.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Course, Enrollment


@receiver(post_save, sender=Course)
def invalidate_course_cache(sender, instance, **kwargs):
    """Invalidate cache for course-related views when a course is saved."""
    cache.delete(f'course_{instance.id}')
    cache.delete('course_list')


@receiver(post_save, sender=Enrollment)
def update_enrollment_count(sender, instance, created, **kwargs):
    """Update course's cached enrollment count when a student enrolls/unenrolls."""
    if created:
        cache.delete(f'course_{instance.course.id}_enrollments')
        cache.delete(f'course_{instance.course.id}')


@receiver(pre_delete, sender=Enrollment)
def handle_unenrollment(sender, instance, **kwargs):
    """Handle unenrollment by invalidating cache."""
    cache.delete(f'course_{instance.course.id}_enrollments')
    cache.delete(f'course_{instance.course.id}')