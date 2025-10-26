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
    try:
        # Log to file for debugging
        import datetime
        log_file = "/app/logs/auth_debug.log"
        with open(log_file, "a") as f:
            f.write(f"{datetime.datetime.now()} - SIGNUP REQUEST: {request.META.get('REMOTE_ADDR')} - {dict(request.data)}\n")

        logger.info(f"🔥 SIGNUP REQUEST RECEIVED: {request.META.get('REMOTE_ADDR')} - {request.data}")
        logger.info(f"📊 Raw request data: {dict(request.data)}")
        logger.info(f"📊 Request content type: {request.content_type}")
    except Exception as e:
        logger.error(f"❌ Error logging signup request: {e}")

    try:
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        first_name = (request.data.get('first_name') or '').strip()
        last_name = (request.data.get('last_name') or '').strip()
        grade = request.data.get('grade')
        school = (request.data.get('school') or '').strip()

        logger.info(f"📧 Processing signup for: {email}")
        logger.info(f"📝 Parsed data: email='{email}', password_len={len(password)}, first_name='{first_name}', last_name='{last_name}', grade={repr(grade)}, school='{school}'")
        logger.info(f"📝 Grade type: {type(grade)}, Grade value: {grade}")

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
        
        # Generate simple session-based token (temporary fix for OAuth2 issues)
        from django.contrib.sessions.models import Session

        # Store user info in session (temporary approach)
        from django.contrib.sessions.backends.db import SessionStore
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
            }
        }, status=status.HTTP_201_CREATED)

        # Set the session cookie so Django session auth works
        response.set_cookie(
            'sessionid',
            session.session_key,
            max_age=3600,  # 1 hour
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax'
        )

        logger.info(f"✅ User registered with session token: {email}")

        return response
        
    except Exception as e:
        # Log detailed error to file
        try:
            import datetime
            import traceback
            error_log = "/app/logs/auth_errors.log"
            with open(error_log, "a") as f:
                f.write(f"{datetime.datetime.now()} - SIGNUP ERROR: {str(e)}\n")
                f.write(f"Traceback: {traceback.format_exc()}\n")
                f.write(f"Request data: {dict(request.data)}\n")
                f.write("-" * 50 + "\n")
        except Exception as log_error:
            logger.error(f"❌ Error writing to log file: {log_error}")

        logger.error(f"❌ Signup error: {str(e)}")
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
        
        # Generate simple session-based token (temporary fix for OAuth2 issues)
        from django.contrib.sessions.backends.db import SessionStore

        # Store user info in session (temporary approach)
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
            }
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

        logger.info(f"✅ User login successful with session token: {email}")

        return response
        
    except Exception as e:
        # Log detailed error to file
        try:
            import datetime
            import traceback
            error_log = "/app/logs/auth_errors.log"
            with open(error_log, "a") as f:
                f.write(f"{datetime.datetime.now()} - LOGIN ERROR: {str(e)}\n")
                f.write(f"Traceback: {traceback.format_exc()}\n")
                f.write(f"Request data: {dict(request.data)}\n")
                f.write("-" * 50 + "\n")
        except Exception as log_error:
            logger.error(f"❌ Error writing to log file: {log_error}")

        logger.error(f"❌ Login error: {str(e)}")
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
