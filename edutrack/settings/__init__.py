"""
Settings module initializer.
"""

import os

# Default to development settings
env = os.environ.get('DJANGO_SETTINGS_MODULE', 'edutrack.settings.development')

if env == 'edutrack.settings.production':
    from .production import *
else:
    from .development import *