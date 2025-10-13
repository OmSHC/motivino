"""
Serializers for users app.
"""
from rest_framework import serializers
from .models import User, Visit


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    initials = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'grade', 'school', 
            'role', 'signup_date', 'last_visit_date', 'visit_days_count', 'initials'
        ]
        read_only_fields = ['id', 'email', 'role', 'signup_date', 'last_visit_date', 'visit_days_count']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'grade', 'school']
    
    def validate_grade(self, value):
        """Validate grade is between 1 and 12."""
        if value is not None and (value < 1 or value > 12):
            raise serializers.ValidationError("Grade must be between 1 and 12.")
        return value


class VisitSerializer(serializers.ModelSerializer):
    """
    Serializer for Visit model.
    """
    class Meta:
        model = Visit
        fields = ['id', 'visited_date', 'created_at']
        read_only_fields = ['id', 'created_at']
