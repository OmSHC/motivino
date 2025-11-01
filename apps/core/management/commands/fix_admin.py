"""
Management command to fix admin user privileges.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Fix admin user privileges for existing superusers'

    def add_arguments(self, parser):
        parser.add_argument('--email', help='Specific admin email to fix (optional)')

    def handle(self, *args, **options):
        email = options.get('email')

        if email:
            # Fix specific user
            try:
                user = User.objects.get(email=email)
                self._fix_user(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with email {email} not found')
                )
        else:
            # Fix all superusers and staff
            superusers = User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True)
            count = 0
            for user in superusers:
                if self._fix_user(user):
                    count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Fixed {count} admin users')
            )

    def _fix_user(self, user):
        """Fix a single user's admin privileges."""
        changed = False

        self.stdout.write(f'Checking user: {user.email}')
        self.stdout.write(f'  Current role: {user.role}')
        self.stdout.write(f'  is_superuser: {user.is_superuser}')
        self.stdout.write(f'  is_staff: {user.is_staff}')
        self.stdout.write(f'  is_admin(): {user.is_admin()}')

        # Ensure superusers and staff have ADMIN role
        if (user.is_superuser or user.is_staff) and user.role != 'ADMIN':
            user.role = 'ADMIN'
            changed = True
            self.stdout.write(f'  → Updated role to ADMIN')

        # Ensure user is active
        if not user.is_active:
            user.is_active = True
            changed = True
            self.stdout.write(f'  → Activated user')

        if changed:
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Fixed admin privileges for: {user.email}')
            )
        else:
            self.stdout.write(f'  → No changes needed for: {user.email}')

        return changed
