# """
# Signal handlers for the users app.
# """

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from django.db import IntegrityError

# from .models import UserProfile


# # Signal to create a profile for admin users or users created outside API
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     """
#     Create a UserProfile for users created outside the API.
#     For API registrations, the profile is created explicitly by RegisterSerializer.
#     """
#     # Only create profiles for users created outside the API
#     # Specifically Django admin or management commands
#     if created and not hasattr(instance, '_skip_signal') and not hasattr(instance, 'profile'):
#         UserProfile.objects.create(user=instance)