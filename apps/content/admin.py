"""
Admin configuration for content app.
"""
from django.contrib import admin
from .models import Content, Comment, Bookmark


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    """
    Admin for Content model.
    """
    list_display = ('content_type', 'title', 'target_grade', 'target_school', 'source', 'published_at', 'is_active')
    list_filter = ('content_type', 'source', 'is_active', 'target_grade', 'created_at', 'published_at')
    search_fields = ('title', 'body', 'target_school')
    date_hierarchy = 'published_at'
    readonly_fields = ('hash', 'created_at')

    fieldsets = (
        ('Content', {
            'fields': ('content_type', 'title', 'body')
        }),
        ('Targeting', {
            'fields': ('target_grade', 'target_school'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('source', 'published_at', 'is_active', 'hash', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin for Comment model.
    """
    list_display = ('user', 'content', 'text', 'created_at', 'is_active')
    list_filter = ('created_at', 'is_active')
    search_fields = ('user__email', 'content__title', 'text')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related('user', 'content')


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """
    Admin for Bookmark model.
    """
    list_display = ('user', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'content__title', 'content__body')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related('user', 'content')
