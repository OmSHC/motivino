"""
Management command to seed initial data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.content.models import Content
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed initial data for the application'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...')
        
        # Create sample admin user if not exists
        admin_email = 'admin@example.com'
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_user(
                email=admin_email,
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='ADMIN',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(f'Created admin user: {admin_email}')
        
        # Create sample regular user
        user_email = 'student@example.com'
        if not User.objects.filter(email=user_email).exists():
            User.objects.create_user(
                username=user_email,  # Use email as username
                email=user_email,
                password='student123',
                first_name='John',
                last_name='Student',
                grade=7,
                school='Example Middle School',
                role='USER'
            )
            self.stdout.write(f'Created sample user: {user_email}')
        
        # Create sample content
        sample_content = [
            {
                'section': 'NEWS',
                'title': 'Young Scientists Win Regional Competition',
                'body': 'Students from grades 6-8 showcased amazing science projects at the regional fair. Their innovative solutions to environmental challenges impressed judges and inspired their peers!',
                'target_grade': 7,
                'source': 'admin'
            },
            {
                'section': 'JOKES',
                'title': None,
                'body': 'Why did the math book look so sad? Because it had too many problems!',
                'target_grade': 5,
                'source': 'admin'
            },
            {
                'section': 'QUOTATION',
                'title': 'Quote by Albert Einstein',
                'body': 'The important thing is not to stop questioning. Curiosity has its own reason for existing.',
                'source': 'admin'
            },
            {
                'section': 'STORY',
                'title': 'The Kindness Chain',
                'body': 'When Sarah helped her classmate with homework, it started a chain reaction. Soon, everyone was helping each other, and their classroom became the most supportive place in the school!',
                'target_grade': 4,
                'source': 'admin'
            }
        ]
        
        created_count = 0
        for item in sample_content:
            if not Content.objects.filter(body=item['body']).exists():
                Content.objects.create(
                    section=item['section'],
                    title=item['title'],
                    body=item['body'],
                    target_grade=item.get('target_grade'),
                    source=item['source'],
                    published_at=timezone.now()
                )
                created_count += 1
        
        if created_count > 0:
            self.stdout.write(f'Created {created_count} sample content items')
        
        self.stdout.write(
            self.style.SUCCESS('Initial data seeding completed successfully!')
        )
