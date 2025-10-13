"""
Management command to generate content manually.
"""
from django.core.management.base import BaseCommand
from apps.core.services import ContentGenerationService


class Command(BaseCommand):
    help = 'Generate motivational content for all grades'

    def add_arguments(self, parser):
        parser.add_argument(
            '--grade',
            type=int,
            help='Generate content for specific grade (1-12)',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='Number of content items to generate per grade',
        )
        parser.add_argument(
            '--quote-only',
            action='store_true',
            help='Generate only daily quote',
        )

    def handle(self, *args, **options):
        service = ContentGenerationService()
        
        if options['quote_only']:
            self.stdout.write('Generating daily quote...')
            success = service.generate_daily_quote()
            if success:
                self.stdout.write(
                    self.style.SUCCESS('Daily quote generated successfully')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to generate daily quote')
                )
        elif options['grade']:
            grade = options['grade']
            count = options['count']
            
            if grade < 1 or grade > 12:
                self.stdout.write(
                    self.style.ERROR('Grade must be between 1 and 12')
                )
                return
            
            self.stdout.write(f'Generating {count} content items for grade {grade}...')
            created_count = service.generate_content_for_grade(grade, count)
            self.stdout.write(
                self.style.SUCCESS(f'Created {created_count} content items for grade {grade}')
            )
        else:
            self.stdout.write('Generating content for all grades...')
            summary = service.generate_content_for_all_grades()
            
            total_created = sum(summary.values())
            self.stdout.write(
                self.style.SUCCESS(f'Content generation completed. Total created: {total_created}')
            )
            
            for key, value in summary.items():
                self.stdout.write(f'  {key}: {value}')
