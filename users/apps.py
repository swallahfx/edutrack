"""
Users app configuration.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for the users app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # def ready(self):
    #     """Import signal handlers when the app is ready."""
    #     import users.signals  # noqa