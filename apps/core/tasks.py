"""
Celery tasks for content generation and scheduling.
"""
from celery import shared_task
from django.utils import timezone
from .services import ContentGenerationService
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_daily_content():
    """
    Daily task to generate motivational content for all grades.
    """
    logger.info("Starting daily content generation task")
    
    try:
        service = ContentGenerationService()
        summary = service.generate_content_for_all_grades()
        
        logger.info(f"Daily content generation completed: {summary}")
        return {
            'status': 'success',
            'summary': summary,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Daily content generation failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def generate_content_for_grade(grade: int, count: int = 3):
    """
    Generate content for a specific grade.
    """
    logger.info(f"Generating content for grade {grade}")
    
    try:
        service = ContentGenerationService()
        created_count = service.generate_content_for_grade(grade, count)
        
        logger.info(f"Generated {created_count} items for grade {grade}")
        return {
            'status': 'success',
            'grade': grade,
            'created_count': created_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Content generation for grade {grade} failed: {e}")
        return {
            'status': 'error',
            'grade': grade,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def generate_daily_quote():
    """
    Generate daily motivational quote.
    """
    logger.info("Generating daily quote")
    
    try:
        service = ContentGenerationService()
        success = service.generate_daily_quote()
        
        logger.info(f"Daily quote generation {'successful' if success else 'failed'}")
        return {
            'status': 'success' if success else 'failed',
            'quote_created': success,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Daily quote generation failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }
