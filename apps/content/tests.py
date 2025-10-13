"""
Tests for content app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Content, Bookmark
import json

User = get_user_model()


class ContentModelTest(TestCase):
    """Test Content model functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        self.content = Content.objects.create(
            content_type='MOTIVATION',
            title='Test News',
            body='This is a test news article.',
            target_grade=7,
            source='admin'
        )
    
    def test_content_creation(self):
        """Test content creation."""
        self.assertEqual(self.content.content_type, 'MOTIVATION')
        self.assertEqual(self.content.title, 'Test News')
        self.assertEqual(self.content.target_grade, 7)
        self.assertTrue(self.content.is_active)
    
    def test_content_hash_generation(self):
        """Test content hash generation for deduplication."""
        self.assertIsNotNone(self.content.hash)
        self.assertEqual(len(self.content.hash), 64)  # SHA-256 hex length
    
    def test_content_for_user_filtering(self):
        """Test content filtering for specific user."""
        # Create content for different grades
        Content.objects.create(
            content_type='MOTIVATION',
            title='Grade 5 News',
            body='Content for grade 5',
            target_grade=5,
            source='admin'
        )
        
        Content.objects.create(
            content_type='MOTIVATION',
            title='General News',
            body='Content for all grades',
            source='admin'
        )
        
        # Test filtering for grade 7 user
        self.user.grade = 7
        self.user.save()
        
        content = Content.get_content_for_user(self.user, content_type='MOTIVATION')
        self.assertEqual(len(content), 2)  # Grade 7 specific + general
        
        # Test filtering for grade 5 user
        self.user.grade = 5
        self.user.save()
        
        content = Content.get_content_for_user(self.user, content_type='MOTIVATION')
        self.assertEqual(len(content), 2)  # Grade 5 specific + general


class BookmarkModelTest(TestCase):
    """Test Bookmark model functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        self.content = Content.objects.create(
            content_type='MOTIVATION',
            title='Test News',
            body='This is a test news article.',
            source='admin'
        )
    
    def test_bookmark_creation(self):
        """Test bookmark creation."""
        bookmark = Bookmark.objects.create(
            user=self.user,
            content=self.content
        )
        
        self.assertEqual(bookmark.user, self.user)
        self.assertEqual(bookmark.content, self.content)
    
    def test_bookmark_unique_constraint(self):
        """Test that users can't bookmark the same content twice."""
        Bookmark.objects.create(user=self.user, content=self.content)
        
        # Try to create duplicate bookmark
        with self.assertRaises(Exception):
            Bookmark.objects.create(user=self.user, content=self.content)


class ContentAPITest(APITestCase):
    """Test Content API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            grade=7,
            school='Test School'
        )
        
        self.content = Content.objects.create(
            content_type='MOTIVATION',
            title='Test News',
            body='This is a test news article.',
            target_grade=7,
            source='admin'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_get_content_list(self):
        """Test getting content list."""
        url = reverse('content:content-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_get_content_detail(self):
        """Test getting specific content."""
        url = reverse('content:content-detail', kwargs={'id': self.content.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test News')
    
    def test_toggle_bookmark(self):
        """Test bookmark toggle functionality."""
        url = reverse('content:toggle-bookmark', kwargs={'content_id': self.content.id})
        
        # First bookmark
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['bookmarked'])
        
        # Remove bookmark
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['bookmarked'])
    
    def test_get_bookmarks(self):
        """Test getting user bookmarks."""
        # Create a bookmark
        Bookmark.objects.create(user=self.user, content=self.content)
        
        url = reverse('content:bookmark-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_daily_quote(self):
        """Test getting daily quote."""
        # Create a quote
        quote = Content.objects.create(
            section='QUOTATION',
            title='Daily Quote',
            body='This is an inspirational quote.',
            source='admin'
        )
        
        url = reverse('content:daily-quote')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['section'], 'QUOTATION')


class ContentAdminAPITest(APITestCase):
    """Test Content Admin API endpoints."""
    
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
        
        self.content = Content.objects.create(
            content_type='MOTIVATION',
            title='Test News',
            body='This is a test news article.',
            source='admin'
        )
    
    def test_admin_create_content(self):
        """Test admin creating content."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('content:admin-content-create')
        data = {
            'section': 'NEWS',
            'title': 'New Article',
            'body': 'This is a new article.',
            'source': 'admin'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_regular_user_cannot_create_content(self):
        """Test that regular users cannot create content."""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('content:admin-content-create')
        data = {
            'section': 'NEWS',
            'title': 'New Article',
            'body': 'This is a new article.',
            'source': 'admin'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_update_content(self):
        """Test admin updating content."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('content:admin-content-update', kwargs={'pk': self.content.id})
        data = {
            'section': 'NEWS',
            'title': 'Updated Article',
            'body': 'This is an updated article.',
            'source': 'admin'
        }
        
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.content.refresh_from_db()
        self.assertEqual(self.content.title, 'Updated Article')
    
    def test_admin_delete_content(self):
        """Test admin deleting content."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('content:admin-content-delete', kwargs={'pk': self.content.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Content.objects.filter(id=self.content.id).exists())
