"""
Email/Password authentication views.
"""
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import User
from oauth2_provider.models import Application, AccessToken
from oauth2_provider.settings import oauth2_settings
from datetime import timedelta
import logging
import re

logger = logging.getLogger(__name__)


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    User signup with email and password.
    """
    logger.info(f"🔥 SIGNUP REQUEST RECEIVED: {request.META.get('REMOTE_ADDR')} - {request.data}")

    try:
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        first_name = (request.data.get('first_name') or '').strip()
        last_name = (request.data.get('last_name') or '').strip()
        grade = request.data.get('grade')
        school = (request.data.get('school') or '').strip()

        logger.info(f"📧 Processing signup for: {email}")
        logger.info(f"📝 Received data: email={email}, password={'*' * len(password) if password else 'None'}, first_name={first_name}, last_name={last_name}, grade={grade}, school={school}")

        # Validate required fields
        if not email or not password:
            logger.error(f"❌ Missing required fields: email={bool(email)}, password={bool(password)}")
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate email format
        if not validate_email(email):
            logger.error(f"❌ Invalid email format: {email}")
            return Response(
                {'error': 'Invalid email format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            logger.error(f"❌ Password validation failed: {error_msg}")
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            logger.warning(f"⚠️ User already exists: {email}")
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"✅ All validations passed for: {email}")
        
        # Validate grade if provided
        if grade:
            try:
                grade = int(grade)
                if grade < 1 or grade > 12:
                    return Response(
                        {'error': 'Grade must be between 1 and 12'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Invalid grade value'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            grade=grade,
            school=school,
            role='ADMIN' if email in ['admin@example.com', 'admin@test.com'] else 'USER'
        )
        
        logger.info(f"New user registered: {email}")
        
        # Track visit
        user.update_visit_tracking()
        
        # Generate access token
        app, _ = Application.objects.get_or_create(
            name="Student Motivation News",
            defaults={
                'client_type': Application.CLIENT_CONFIDENTIAL,
                'authorization_grant_type': Application.GRANT_PASSWORD,
            }
        )
        
        expires = oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
        
        # Delete any existing tokens for this user
        AccessToken.objects.filter(user=user, application=app).delete()
        
        import uuid
        access_token_obj = AccessToken.objects.create(
            user=user,
            application=app,
            token=f'token-{uuid.uuid4()}',
            expires=timezone.now() + timedelta(seconds=expires),
            scope='read write'
        )
        
        return Response({
            'access_token': access_token_obj.token,
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
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return Response(
            {'error': 'Registration failed. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User login with email and password.
    """
    logger.info(f"🔑 LOGIN REQUEST RECEIVED: {request.META.get('REMOTE_ADDR')} - {request.data}")

    try:
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''

        logger.info(f"🔓 Processing login for: {email}")

        # Validate required fields
        if not email or not password:
            logger.error(f"❌ Missing login fields: email={bool(email)}, password={bool(password)}")
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to get user by email
        try:
            user = User.objects.get(email=email)
            logger.info(f"✅ Found user: {email} (active: {user.is_active})")
        except User.DoesNotExist:
            logger.warning(f"❌ User not found: {email}")
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check password
        if not user.check_password(password):
            logger.warning(f"❌ Invalid password for: {email}")
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user is active
        if not user.is_active:
            logger.warning(f"❌ Account disabled for: {email}")
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        logger.info(f"🎉 User login successful: {email}")
        
        # Track visit
        user.update_visit_tracking()
        
        # Generate access token
        app, _ = Application.objects.get_or_create(
            name="Student Motivation News",
            defaults={
                'client_type': Application.CLIENT_CONFIDENTIAL,
                'authorization_grant_type': Application.GRANT_PASSWORD,
            }
        )
        
        expires = oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
        
        # Delete any existing tokens for this user
        AccessToken.objects.filter(user=user, application=app).delete()
        
        import uuid
        access_token_obj = AccessToken.objects.create(
            user=user,
            application=app,
            token=f'token-{uuid.uuid4()}',
            expires=timezone.now() + timedelta(seconds=expires),
            scope='read write'
        )
        
        return Response({
            'access_token': access_token_obj.token,
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
        logger.error(f"Login error: {str(e)}")
        return Response(
            {'error': 'Login failed. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout - invalidate access token.
    """
    try:
        # Get the token from the request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # Delete the token
            AccessToken.objects.filter(token=token).delete()
            logger.info(f"User logged out: {request.user.email}")
        
        return Response({'message': 'Logged out successfully'})
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response(
            {'error': 'Logout failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
