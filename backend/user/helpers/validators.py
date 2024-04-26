from ..models import CustomUser
from rest_framework import serializers

def is_not_registered(email):
    if CustomUser.objects.filter(email=email).exists():
        raise serializers.ValidationError("Email is already registered.")
    return email

def is_registered(email):
    if not CustomUser.objects.filter(email=email).exists():
        raise serializers.ValidationError("Email not registered.")
    return email

def validate_password(value):
        # Custom password validation
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters.')

        has_letter = any(char.isalpha() for char in value)
        has_digit = any(char.isdigit() for char in value)

        if not (has_letter and has_digit):
            raise serializers.ValidationError('The password must contain at least one letter and one number.')

        return value

def validate_register_type(value):
        if value not in ('email', 'google'):
            raise serializers.ValidationError('Invalid register type. Must be "email" or "google".')
        return value