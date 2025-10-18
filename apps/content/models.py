"""
Content models for the motivation news application.
"""
import uuid
import hashlib
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Content(models.Model):
    """
    Model for storing motivational content (news, jokes, quotations, stories).
    """
    CONTENT_TYPE_CHOICES = [
        ('MOTIVATION', 'Motivation'),
        ('JOKES', 'Jokes'),
        ('QUOTATION', 'Quotation'),
        ('PUZZLE', 'Puzzle'),
    ]
    
    RESUBMISSION_STATUS_CHOICES = [
        ('none', 'Not Resubmitted'),
        ('resubmitted', 'Resubmitted'),
        ('original', 'Original Version'),
    ]

    SOURCE_CHOICES = [
        ('openai', 'OpenAI'),
        ('admin', 'Admin'),
        ('user', 'User Submitted'),
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='MOTIVATION')
    title = models.CharField(max_length=255, null=True, blank=True)
    body = models.TextField()
    rich_content = models.TextField(null=True, blank=True, help_text="Rich text HTML content")
    youtube_url = models.URLField(null=True, blank=True, help_text="YouTube video URL")
    news_url = models.URLField(null=True, blank=True, help_text="News article URL")
    target_grade = models.IntegerField(null=True, blank=True, help_text="Target grade (1-12)")
    target_school = models.CharField(max_length=255, null=True, blank=True, help_text="Target school")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='admin')
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    hash = models.CharField(max_length=64, unique=True, help_text="SHA-256 hash for deduplication")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_content')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_content', help_text="User who submitted this content")
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='approved', help_text="Approval status for user-submitted content")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_content', help_text="Admin who reviewed this content")
    reviewed_at = models.DateTimeField(null=True, blank=True, help_text="When the content was reviewed")
    rejection_reason = models.TextField(null=True, blank=True, help_text="Reason for rejection if content was rejected")
    resubmission_status = models.CharField(max_length=20, choices=RESUBMISSION_STATUS_CHOICES, default='none')
    original_submission = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='resubmissions')
    
    class Meta:
        db_table = 'content'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['content_type', 'published_at']),
            models.Index(fields=['target_grade', 'content_type']),
            models.Index(fields=['target_school', 'content_type']),
            models.Index(fields=['hash']),
        ]
        verbose_name = 'Content'
        verbose_name_plural = 'Content'
    
    def __str__(self):
        return f"{self.content_type}: {self.title or self.body[:50]}"
    
    def save(self, *args, **kwargs):
        """Override save to generate hash for deduplication."""
        if not self.hash:
            self.hash = self.generate_hash()
        super().save(*args, **kwargs)
    
    def generate_hash(self):
        """Generate SHA-256 hash for deduplication."""
        content = (self.title or '') + (self.body or '')
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @classmethod
    def get_content_for_user(cls, user, content_type='MOTIVATION', limit=20, offset=0):
        """
        Get content filtered for a specific user's grade and school.
        Only shows approved content.
        """
        if content_type == 'MIXED':
            # For MIXED content, get from MOTIVATION content type for homepage
            queryset = cls.objects.filter(
                content_type='MOTIVATION',
                is_active=True,
                approval_status='approved',  # Only show approved content
                published_at__lte=timezone.now()
            )
        else:
            queryset = cls.objects.filter(
                content_type=content_type,
                is_active=True,
                approval_status='approved',  # Only show approved content
                published_at__lte=timezone.now()
            )
        
        # Filter by grade if user has a grade
        if user.grade:
            queryset = queryset.filter(
                models.Q(target_grade__isnull=True) | models.Q(target_grade=user.grade)
            )

        # Filter by school if user has a school
        if user.school:
            queryset = queryset.filter(
                models.Q(target_school__isnull=True) | models.Q(target_school=user.school)
            )

        return queryset[offset:offset + limit]


class Comment(models.Model):
    """
    Model for content comments.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'comment'
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"{self.user.email}: {self.text[:50]}"


class Bookmark(models.Model):
    """
    Model for user bookmarks.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'bookmarks'
        unique_together = ['user', 'content']
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'

    def __str__(self):
        return f"{self.user.email} bookmarked {self.content}"
