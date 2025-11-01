"""
User models for the motivation news application.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    grade = models.IntegerField(null=True, blank=True, help_text="Student grade (1-12)")
    school = models.CharField(max_length=255, null=True, blank=True, help_text="School name")
    role = models.CharField(
        max_length=20,
        choices=[('USER', 'User'), ('ADMIN', 'Admin')],
        default='USER'
    )
    signup_date = models.DateTimeField(default=timezone.now)
    last_visit_date = models.DateField(null=True, blank=True)
    visit_days_count = models.IntegerField(default=0)

    # Override username to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is used as username, no additional required fields
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    @property
    def initials(self):
        """Get user initials for avatar display."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        elif self.email:
            return self.email[0].upper()
        return "U"

    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'ADMIN' or self.is_staff or self.is_superuser

    def save(self, *args, **kwargs):
        """Override save to ensure superusers have admin role."""
        # Auto-set role to ADMIN for superusers and staff
        if (self.is_superuser or self.is_staff) and self.role != 'ADMIN':
            self.role = 'ADMIN'
        super().save(*args, **kwargs)

    def update_visit_tracking(self):
        """Update visit tracking for the current day."""
        today = timezone.now().date()
        
        if self.last_visit_date != today:
            self.last_visit_date = today
            self.visit_days_count += 1
            self.save(update_fields=['last_visit_date', 'visit_days_count'])
            
            # Create visit record
            Visit.objects.get_or_create(
                user=self,
                visited_date=today,
                defaults={'created_at': timezone.now()}
            )


class Visit(models.Model):
    """
    Track user visits by date.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visits')
    visited_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'visits'
        unique_together = ['user', 'visited_date']
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'
    
    def __str__(self):
        return f"{self.user.email} - {self.visited_date}"
