"""
Management command to initialize database directory and file.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Initialize database directory and file for SQLite'

    def handle(self, *args, **options):
        # Get database path from settings
        db_path = settings.DATABASES['default']['NAME']

        self.stdout.write(f'Initializing database at: {db_path}')

        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            self.stdout.write(f'Creating directory: {db_dir}')
            os.makedirs(db_dir, exist_ok=True)
        else:
            self.stdout.write(f'Directory exists: {db_dir}')

        # Ensure database file exists
        if not os.path.exists(db_path):
            self.stdout.write(f'Creating database file: {db_path}')
            open(db_path, 'a').close()
        else:
            self.stdout.write(f'Database file exists: {db_path}')

        # Set proper permissions
        try:
            os.chmod(db_dir, 0o755)
            os.chmod(db_path, 0o644)
            self.stdout.write('Set proper permissions')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not set permissions: {e}'))

        # Verify database is accessible
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('Database is accessible'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Database access failed: {e}'))

        self.stdout.write(self.style.SUCCESS('Database initialization complete'))
