"""
Utility functions for the edutrack project.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError


def custom_exception_handler(exc, context):
    """
    Custom exception handler for the API.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If response is already handled by DRF, just return it
    if response is not None:
        return response

    # Handle custom exceptions
    if isinstance(exc, IntegrityError):
        data = {'detail': 'Database integrity error occurred.'}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    # Default to 500 error for unhandled exceptions
    return Response(
        {'detail': 'A server error occurred.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )