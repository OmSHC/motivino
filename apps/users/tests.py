"""
Tests for users app.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            grade=7,
            school='Test School'
        )
    
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.grade, 7)
        self.assertEqual(self.user.role, 'USER')
    
    def test_user_initials(self):
        """Test user initials generation."""
        self.assertEqual(self.user.initials, 'TU')
        
        # Test with only first name
        self.user.last_name = ''
        self.user.save()
        self.assertEqual(self.user.initials, 'T')
        
        # Test with only email
        self.user.first_name = ''
        self.user.save()
        self.assertEqual(self.user.initials, 'T')
    
    def test_user_admin_check(self):
        """Test admin role checking."""
        self.assertFalse(self.user.is_admin())
        
        self.user.role = 'ADMIN'
        self.user.save()
        self.assertTrue(self.user.is_admin())
        
        self.user.role = 'USER'
        self.user.is_staff = True
        self.user.save()
        self.assertTrue(self.user.is_admin())
    
    def test_visit_tracking(self):
        """Test visit tracking functionality."""
        today = timezone.now().date()
        
        # First visit
        self.user.update_visit_tracking()
        self.assertEqual(self.user.visit_days_count, 1)
        self.assertEqual(self.user.last_visit_date, today)
        
        # Same day visit (should not increment)
        self.user.update_visit_tracking()
        self.assertEqual(self.user.visit_days_count, 1)
        
        # Next day visit
        self.user.last_visit_date = today - timezone.timedelta(days=1)
        self.user.save()
        self.user.update_visit_tracking()
        self.assertEqual(self.user.visit_days_count, 2)


class UserAPITest(APITestCase):
    """Test User API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            grade=7,
            school='Test School'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_current_user(self):
        """Test getting current user."""
        url = reverse('users:current-user')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['grade'], 7)
    
    def test_update_user_profile(self):
        """Test updating user profile."""
        url = reverse('users:update-user')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'grade': 8,
            'school': 'Updated School'
        }
        
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.grade, 8)
    
    def test_update_user_invalid_grade(self):
        """Test updating user with invalid grade."""
        url = reverse('users:update-user')
        data = {'grade': 15}  # Invalid grade
        
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_track_visit(self):
        """Test visit tracking endpoint."""
        url = reverse('users:track-visit')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.visit_days_count, 1)


class UserAuthenticationTest(APITestCase):
    """Test user authentication."""
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        url = reverse('users:current-user')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_oauth_callback_missing_code(self):
        """Test OAuth callback without authorization code."""
        url = reverse('users:google-oauth-callback')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Authorization code not provided', response.data['error'])
