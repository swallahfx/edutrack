"""
Custom token views for JWT authentication.
"""

import logging
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer to add logging."""
    
    def validate(self, attrs):
        """Override validate to add logging."""
        try:
            logger.info(f"Login attempt for user: {attrs.get('username')}")
            data = super().validate(attrs)
            logger.info(f"Login successful for user: {attrs.get('username')}")
            return data
        except Exception as e:
            logger.error(f"Login failed for user: {attrs.get('username')}, Error: {str(e)}")
            raise

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view to add logging."""
    
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """Override post to add more logging."""
        logger.info("TokenObtainPairView.post called")
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"TokenObtainPairView.post success: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"TokenObtainPairView.post error: {str(e)}")
            return Response(
                {"error": f"Login failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view to add logging."""
    
    def post(self, request, *args, **kwargs):
        """Override post to add more logging."""
        logger.info("TokenRefreshView.post called")
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"TokenRefreshView.post success: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"TokenRefreshView.post error: {str(e)}")
            return Response(
                {"error": f"Token refresh failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )