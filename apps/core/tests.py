"""
Tests for core app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
import json

User = get_user_model()


class CoreAPITest(APITestCase):
    """Test Core API endpoints."""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='adminpass123',
            role='ADMIN',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user@example.com',
            email='user@example.com',
            password='userpass123'
        )
    
    def test_homepage_view(self):
        """Test homepage view."""
        url = reverse('core:homepage')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Welcome to Student Motivation News', response.content.decode())
    
    def test_api_docs_view(self):
        """Test API documentation view."""
        url = reverse('core:api-docs')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('title', data)
        self.assertIn('endpoints', data)
    
    @patch('apps.core.views.generate_daily_content')
    def test_trigger_content_generation_admin(self, mock_task):
        """Test content generation trigger by admin."""
        mock_task.delay.return_value = MagicMock(id='test-task-id')
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('core:generate-content')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Content generation started', response.data['message'])
        self.assertEqual(response.data['task_id'], 'test-task-id')
        mock_task.delay.assert_called_once()
    
    def test_trigger_content_generation_regular_user(self):
        """Test that regular users cannot trigger content generation."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('core:generate-content')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Admin access required', response.data['error'])
    
    @patch('apps.core.views.generate_content_for_grade')
    def test_trigger_grade_content_generation(self, mock_task):
        """Test grade-specific content generation."""
        mock_task.delay.return_value = MagicMock(id='test-task-id')
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('core:generate-grade-content')
        data = {'grade': 7, 'count': 3}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Content generation for grade 7 started', response.data['message'])
        mock_task.delay.assert_called_once_with(7, 3)
    
    def test_trigger_grade_content_generation_invalid_grade(self):
        """Test grade content generation with invalid grade."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('core:generate-grade-content')
        data = {'grade': 15}  # Invalid grade
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Valid grade (1-12) required', response.data['error'])
    
    @patch('apps.core.views.generate_daily_quote')
    def test_trigger_quote_generation(self, mock_task):
        """Test daily quote generation."""
        mock_task.delay.return_value = MagicMock(id='test-task-id')
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('core:generate-quote')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Daily quote generation started', response.data['message'])
        mock_task.delay.assert_called_once()


class OpenAIServiceTest(TestCase):
    """Test OpenAI service functionality."""
    
    def setUp(self):
        from apps.core.services import OpenAIService
        self.service = OpenAIService(api_key='test-key')
    
    @patch('apps.core.services.OpenAI')
    def test_generate_content_for_grade(self, mock_openai):
        """Test content generation for specific grade."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps([
            {
                "title": "Test News",
                "body": "This is test content for grade 7.",
                "category": "achievement",
                "ageRange": "grade 7"
            }
        ])
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        result = self.service.generate_content_for_grade(7, 1)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Test News')
        self.assertEqual(result[0]['grade'], 7)
    
    @patch('apps.core.services.OpenAI')
    def test_generate_daily_quote(self, mock_openai):
        """Test daily quote generation."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "body": "Education is the most powerful weapon.",
            "source": "Nelson Mandela"
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        result = self.service.generate_daily_quote()
        
        self.assertEqual(result['body'], 'Education is the most powerful weapon.')
        self.assertEqual(result['source'], 'Nelson Mandela')
    
    def test_generate_content_no_api_key(self):
        """Test content generation without API key."""
        service = OpenAIService(api_key=None)
        
        result = service.generate_content_for_grade(7, 1)
        self.assertEqual(result, [])
        
        result = service.generate_daily_quote()
        self.assertEqual(result, {})
    
    @patch('apps.core.services.OpenAI')
    def test_generate_content_api_error(self, mock_openai):
        """Test content generation with API error."""
        mock_openai.return_value.chat.completions.create.side_effect = Exception('API Error')
        
        result = self.service.generate_content_for_grade(7, 1)
        self.assertEqual(result, [])
        
        result = self.service.generate_daily_quote()
        self.assertEqual(result, {})
