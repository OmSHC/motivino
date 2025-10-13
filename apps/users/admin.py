"""
Admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Visit


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model.
    """
    list_display = ('email', 'first_name', 'last_name', 'grade', 'school', 'role', 'visit_days_count', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff', 'grade', 'school')
    search_fields = ('email', 'first_name', 'last_name', 'school')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'grade', 'school')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'signup_date', 'last_visit_date')}),
        ('Visit tracking', {'fields': ('visit_days_count',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'grade', 'school', 'role'),
        }),
    )
    
    readonly_fields = ('signup_date', 'last_visit_date', 'visit_days_count')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    """
    Admin for Visit model.
    """
    list_display = ('user', 'visited_date', 'created_at')
    list_filter = ('visited_date', 'created_at')
    search_fields = ('user__email',)
    date_hierarchy = 'visited_date'
    readonly_fields = ('created_at',)
