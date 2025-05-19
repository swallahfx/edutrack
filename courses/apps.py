"""
Courses app configuration.
"""

from django.apps import AppConfig


class CoursesConfig(AppConfig):
    """Configuration for the courses app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'

    def ready(self):
        """Import signal handlers when the app is ready."""
        import courses.signals  # noqa