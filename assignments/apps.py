"""
Assignments app configuration.
"""

from django.apps import AppConfig


class AssignmentsConfig(AppConfig):
    """Configuration for the assignments app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assignments'

    def ready(self):
        """Import signal handlers when the app is ready."""
        import assignments.signals  # noqa