"""
Core services for OpenAI integration and content generation.
"""
import json
import logging
import hashlib
from typing import List, Dict, Any
from django.conf import settings
from django.utils import timezone
from apps.content.models import Content
from apps.users.models import User

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Service for interacting with OpenAI API.
    """
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
    
    def generate_motivational_content(self, grade: int, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate motivational content for a specific grade.
        """
        if not self.api_key:
            logger.error("OpenAI API key not configured")
            return []
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            system_prompt = (
                "You are a cheerful editor writing short motivational news blurbs for school students. "
                "Your content should be uplifting, age-appropriate, non-political, and non-religious. "
                "Focus on achievements, kindness, science, and positive news that inspires students."
            )
            
            user_prompt = (
                f"Generate {count} short motivational news blurbs for grade {grade}. "
                "Format output as JSON array with objects: "
                '{"title":"...","body":"...","category":"achievement|kindness|science","ageRange":"grade ' + str(grade) + '"} '
                "Each body must be <=220 characters. "
                "Tone: encouraging, age-appropriate, non-political, non-religious. "
                "Avoid real private data and violent content."
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"OpenAI response for grade {grade}: {content}")
            
            # Parse JSON response
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    return data
                else:
                    logger.error(f"Expected list, got {type(data)}")
                    return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                return []
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return []
    
    def generate_daily_quote(self) -> Dict[str, Any]:
        """
        Generate a daily motivational quote.
        """
        if not self.api_key:
            logger.error("OpenAI API key not configured")
            return {}
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            system_prompt = (
                "You are a wise mentor creating inspirational quotes for students. "
                "Your quotes should be uplifting, age-appropriate, and encourage learning and growth."
            )
            
            user_prompt = (
                "Generate one short motivational quote for students (grades 1-12). "
                "Format as JSON: {\"body\":\"Your quote here\",\"source\":\"Author or Unknown\"} "
                "Keep the quote under 100 characters and make it inspiring for young learners."
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"OpenAI quote response: {content}")
            
            try:
                data = json.loads(content)
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse quote response as JSON: {e}")
                return {}
                
        except Exception as e:
            logger.error(f"OpenAI API error for quote: {e}")
            return {}


class ContentGenerationService:
    """
    Service for generating and storing content.
    """
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    def generate_content_for_grade(self, grade: int, count: int = 3) -> int:
        """
        Generate and store content for a specific grade.
        Returns number of items created.
        """
        logger.info(f"Generating content for grade {grade}")
        
        # Generate content from OpenAI
        content_items = self.openai_service.generate_motivational_content(grade, count)
        
        created_count = 0
        for item in content_items:
            try:
                # Sanitize and validate content
                title = self._sanitize_text(item.get('title', ''))
                body = self._sanitize_text(item.get('body', ''))
                
                if not body:
                    logger.warning(f"Empty body for grade {grade} item: {item}")
                    continue
                
                # Check for duplicates using hash
                content_hash = self._generate_hash(title, body)
                if Content.objects.filter(hash=content_hash).exists():
                    logger.info(f"Duplicate content found for grade {grade}, skipping")
                    continue
                
                # Create content record
                content = Content.objects.create(
                    section='NEWS',
                    title=title if title else None,
                    body=body,
                    target_grade=grade,
                    source='openai',
                    published_at=timezone.now(),
                    hash=content_hash
                )
                
                created_count += 1
                logger.info(f"Created content for grade {grade}: {content.id}")
                
            except Exception as e:
                logger.error(f"Error creating content for grade {grade}: {e}")
                continue
        
        logger.info(f"Created {created_count} content items for grade {grade}")
        return created_count
    
    def generate_daily_quote(self) -> bool:
        """
        Generate and store daily quote.
        Returns True if quote was created.
        """
        logger.info("Generating daily quote")
        
        quote_data = self.openai_service.generate_daily_quote()
        if not quote_data:
            logger.error("Failed to generate quote")
            return False
        
        try:
            body = self._sanitize_text(quote_data.get('body', ''))
            source = self._sanitize_text(quote_data.get('source', 'Unknown'))
            
            if not body:
                logger.error("Empty quote body")
                return False
            
            # Check for duplicates
            content_hash = self._generate_hash('', body)
            if Content.objects.filter(hash=content_hash).exists():
                logger.info("Duplicate quote found, skipping")
                return False
            
            # Create quote record
            content = Content.objects.create(
                section='QUOTATION',
                title=f"Quote by {source}",
                body=body,
                source='openai',
                published_at=timezone.now(),
                hash=content_hash
            )
            
            logger.info(f"Created daily quote: {content.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating daily quote: {e}")
            return False
    
    def generate_content_for_all_grades(self) -> Dict[str, int]:
        """
        Generate content for all grades (1-12).
        Returns summary of created items.
        """
        logger.info("Starting content generation for all grades")
        
        summary = {}
        total_created = 0
        
        for grade in range(1, 13):
            created_count = self.generate_content_for_grade(grade)
            summary[f'grade_{grade}'] = created_count
            total_created += created_count
        
        # Generate daily quote
        quote_created = self.generate_daily_quote()
        summary['daily_quote'] = 1 if quote_created else 0
        total_created += summary['daily_quote']
        
        logger.info(f"Content generation complete. Total created: {total_created}")
        return summary
    
    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text content.
        """
        if not text:
            return ''
        
        # Basic sanitization - remove potentially harmful content
        text = text.strip()
        
        # Remove any HTML tags
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        # Limit length
        if len(text) > 500:
            text = text[:500] + '...'
        
        return text
    
    def _generate_hash(self, title: str, body: str) -> str:
        """
        Generate hash for content deduplication.
        """
        content = (title or '') + (body or '')
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
