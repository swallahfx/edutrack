"""
Signal handlers for the assignments app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import Assignment, Submission


@receiver(post_save, sender=Assignment)
def invalidate_assignment_cache(sender, instance, **kwargs):
    """Invalidate cache for assignment-related views when an assignment is saved."""
    cache.delete(f'assignment_{instance.id}')
    cache.delete(f'course_{instance.course.id}_assignments')


@receiver(post_save, sender=Submission)
def handle_submission(sender, instance, created, **kwargs):
    """Handle submission by invalidating cache and updating counts."""
    cache.delete(f'submission_{instance.id}')
    cache.delete(f'assignment_{instance.assignment.id}_submissions')
    
    # Update submission count for the assignment
    cache.delete(f'assignment_{instance.assignment.id}')