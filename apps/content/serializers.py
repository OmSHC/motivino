"""
Serializers for content app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Content, Comment, Bookmark

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model to get name information.
    """
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_name', 'text', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def get_user_name(self, obj):
        """Get the name of the user who created the comment."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return 'Anonymous'

class ContentSerializer(serializers.ModelSerializer):
    """
    Serializer for Content model.
    """
    is_bookmarked = serializers.SerializerMethodField()
    submitted_by_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = [
            'id', 'content_type', 'title', 'body', 'rich_content', 'youtube_url', 'news_url',
            'target_grade', 'target_school', 'source', 'published_at',
            'created_at', 'is_bookmarked', 'is_active', 'created_by', 'submitted_by',
            'submitted_by_name', 'created_by_name', 'approval_status', 'reviewed_by', 'reviewed_at'
        ]
        read_only_fields = ['id', 'created_at', 'hash', 'is_active', 'created_by', 'submitted_by', 'reviewed_by', 'reviewed_at']
    
    def get_is_bookmarked(self, obj):
        """Check if current user has bookmarked this content."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False

    def get_submitted_by_name(self, obj):
        """Get the name of the user who submitted this content."""
        if obj.submitted_by:
            return f"{obj.submitted_by.first_name} {obj.submitted_by.last_name}".strip()
        return None

    def get_created_by_name(self, obj):
        """Get the name of the user who created this content."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None


class ContentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating content (admin only).
    """
    class Meta:
        model = Content
        fields = [
            'content_type', 'title', 'body', 'rich_content', 'youtube_url', 'news_url',
            'target_grade', 'target_school', 'source', 'published_at'
        ]
    
    def validate_target_grade(self, value):
        """Validate grade is between 1 and 12."""
        if value is not None and (value < 1 or value > 12):
            raise serializers.ValidationError("Grade must be between 1 and 12.")
        return value
    
    def validate_youtube_url(self, value):
        """Validate YouTube URL format."""
        if value and 'youtube.com' not in value and 'youtu.be' not in value:
            raise serializers.ValidationError("Please provide a valid YouTube URL.")
        return value


class BookmarkSerializer(serializers.ModelSerializer):
    """
    Serializer for Bookmark model.
    """
    content = ContentSerializer(read_only=True)
    
    class Meta:
        model = Bookmark
        fields = ['id', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']
