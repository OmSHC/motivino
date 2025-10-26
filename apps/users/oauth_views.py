"""
OAuth2 views for Google authentication.
"""
import requests
from django.conf import settings
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import User
import json
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_oauth_callback(request):
    """
    Handle Google OAuth2 callback and create/login user.
    """
    try:
        # Get the authorization code from the request
        code = request.data.get('code')
        if not code:
            return Response(
                {'error': 'Authorization code not provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Exchange code for access token
        token_data = {
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': getattr(settings, 'GOOGLE_REDIRECT_URI', 'http://127.0.0.1:3000/auth/callback'),
        }
        
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data
        )
        
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            return Response(
                {'error': 'Failed to exchange authorization code'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token_info = token_response.json()
        access_token = token_info.get('access_token')
        
        # Get user info from Google
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_info_response.status_code != 200:
            logger.error(f"User info fetch failed: {user_info_response.text}")
            return Response(
                {'error': 'Failed to fetch user information'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_info = user_info_response.json()
        
        # Create or get user
        email = user_info.get('email')
        if not email:
            return Response(
                {'error': 'Email not provided by Google'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
                'role': 'USER',
            }
        )
        
        if created:
            logger.info(f"Created new user: {email}")
        else:
            # Update existing user info
            user.first_name = user_info.get('given_name', user.first_name)
            user.last_name = user_info.get('family_name', user.last_name)
            user.save()
            logger.info(f"Updated existing user: {email}")
        
        # Track visit
        user.update_visit_tracking()
        
        # Generate or get OAuth2 token for API access
        from oauth2_provider.models import Application, AccessToken
        from oauth2_provider.settings import oauth2_settings
        from datetime import timedelta
        
        # Get or create OAuth2 application
        app, _ = Application.objects.get_or_create(
            name="Student Motivation News",
            defaults={
                'client_type': Application.CLIENT_CONFIDENTIAL,
                'authorization_grant_type': Application.GRANT_PASSWORD,
            }
        )
        
        # Create access token
        expires = oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
        access_token_obj = AccessToken.objects.create(
            user=user,
            application=app,
            token=access_token,
            expires=timezone.now() + timedelta(seconds=expires),
            scope='read write'
        )
        
        return Response({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': expires,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'grade': user.grade,
                'school': user.school,
                'role': user.role,
                'visit_days_count': user.visit_days_count,
                'initials': user.initials,
            }
        })
        
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return Response(
            {'error': 'Authentication failed'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def demo_login(request):
    """
    Demo login endpoint for testing without Google OAuth.
    """
    try:
        email = request.data.get('email', 'demo@example.com')
        first_name = request.data.get('first_name', 'Demo')
        last_name = request.data.get('last_name', 'User')
        
        # Create or get demo user
        # Check if this should be an admin user
        is_admin_email = email in ['admin@example.com', 'admin@test.com']
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': 'ADMIN' if is_admin_email else 'USER',
            }
        )
        
        if created:
            logger.info(f"Created demo user: {email} with role: {user.role}")
        else:
            # Update existing user info (preserve role unless it's an admin email)
            user.first_name = first_name
            user.last_name = last_name
            if is_admin_email and user.role != 'ADMIN':
                user.role = 'ADMIN'
            user.save()
            logger.info(f"Updated demo user: {email} with role: {user.role}")
        
        # Track visit
        user.update_visit_tracking()
        
        # Generate session-based token for consistency with main login
        from django.contrib.sessions.backends.db import SessionStore

        # Store user info in session
        session = SessionStore()
        session['user_id'] = str(user.id)
        session['user_email'] = user.email
        session['authenticated'] = True
        session.create()

        # Use the actual session key as the token
        token = session.session_key

        # Set the session cookie in the response
        response = Response({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': 3600,  # 1 hour
            'session_key': session.session_key,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'grade': user.grade,
                'school': user.school,
                'role': user.role,
                'visit_days_count': user.visit_days_count,
                'initials': user.initials,
            },
            'demo_mode': True
        }, status=status.HTTP_200_OK)

        # Set the session cookie so Django session auth works
        response.set_cookie(
            'sessionid',
            session.session_key,
            max_age=3600,  # 1 hour
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax'
        )

        return response
        
    except Exception as e:
        logger.error(f"Demo login error: {str(e)}")
        return Response(
            {'error': 'Demo login failed'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_url(request):
    """
    Get Google OAuth2 authorization URL.
    """
    try:
        client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
        redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', 'http://127.0.0.1:3000/auth/callback')
        
        # Check if we have demo credentials
        if client_id == 'your-google-client-id' or not client_id:
            # Return demo mode response
            return Response({
                'auth_url': 'demo-mode',
                'client_id': 'demo-client-id',
                'redirect_uri': redirect_uri,
                'demo_mode': True,
                'message': 'Demo mode - Google OAuth2 not configured. Please set up Google Cloud Console credentials.'
            })
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=openid%20email%20profile&"
            f"response_type=code&"
            f"access_type=offline"
        )
        
        return Response({
            'auth_url': auth_url,
            'client_id': client_id,
            'redirect_uri': redirect_uri
        })
        
    except Exception as e:
        logger.error(f"OAuth URL generation error: {str(e)}")
        return Response(
            {'error': 'Failed to generate OAuth URL'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
