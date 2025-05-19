"""
Serializers for the users app.
"""

import traceback
import logging
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db import transaction

from .models import UserProfile

# Set up logger
logger = logging.getLogger(__name__)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for the UserProfile model."""
    
    class Meta:
        model = UserProfile
        fields = ['role', 'bio', 'profile_picture', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model with nested profile."""
    
    profile = UserProfileSerializer(required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']
    
    def update(self, instance, validated_data):
        """Update User and nested UserProfile."""
        profile_data = validated_data.pop('profile', None)
        
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update UserProfile fields
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        write_only=True,  # Mark as write_only to prevent read attempt
        required=True,
        choices=UserProfile.ROLE_CHOICES
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'role']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create a new user with the validated data."""
        try:
            with transaction.atomic():
                # Extract role before creating user
                role = validated_data.pop('role')

                if User.objects.filter(username=validated_data['username']).exists():
                    raise serializers.ValidationError({"username": "Username already exists."})
                if User.objects.filter(email=validated_data['email']).exists():
                    raise serializers.ValidationError({"email": "Email already exists."})
                
                # Create user without profile first
                user = User.objects.create(
                    username=validated_data['username'],
                    email=validated_data['email'],
                    first_name=validated_data.get('first_name', ''),
                    last_name=validated_data.get('last_name', '')
                )
                user.set_password(validated_data['password'])
                user.save()
                
                
                try:
                    # Check if profile exists
                    profile = UserProfile.objects.get(user=user)
                    profile.role = role
                    profile.save()
                except UserProfile.DoesNotExist:
                    # Create profile if it doesn't exist
                    logger.info(f"Creating new profile for user {user.id}")
                    UserProfile.objects.create(user=user, role=role)
                
                return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            logger.error(traceback.format_exc())
            raise serializers.ValidationError({"error": str(e)})
    
    def to_representation(self, instance):
        """
        Override to return proper user data after registration.
        This avoids trying to access 'role' directly on the user object.
        """
        # Use UserSerializer to generate the proper representation
        user_serializer = UserSerializer(instance)
        return user_serializer.data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    
    def validate_old_password(self, value):
        """Validate that the old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value