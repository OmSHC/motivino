"""
Custom authentication backends for the application.
"""
from django.contrib.sessions.models import Session
from django.utils import timezone
from rest_framework import authentication, exceptions
from .models import User
import logging

logger = logging.getLogger(__name__)


class SessionTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication backend for session-based tokens.
    Validates tokens in the format: "session-{uuid}"
    """

    def authenticate(self, request):
        """
        Authenticate using session token from Authorization header.
        """
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:
            # Expected format: "Bearer {session_key}" (session key can be with or without "session-" prefix)
            auth_type, token = auth_header.split(' ', 1)

            if auth_type.lower() != 'bearer':
                return None

            # Handle both formats: "session-{uuid}" and direct session keys
            if token.startswith('session-'):
                session_uuid = token[8:]  # Remove 'session-' prefix
            else:
                session_uuid = token  # Use directly as session key

            # Find the session with this key
            try:
                session = Session.objects.get(session_key=session_uuid)

                # Check if session is not expired
                if session.expire_date and session.expire_date < timezone.now():
                    logger.warning(f"Session expired: {session_uuid}")
                    return None

                # Get user data from session
                user_id = session.get_decoded().get('user_id')
                user_email = session.get_decoded().get('user_email')

                if not user_id or not user_email:
                    logger.warning(f"Invalid session data: {session_uuid}")
                    return None

                # Get the user
                try:
                    user = User.objects.get(id=user_id, email=user_email, is_active=True)
                    logger.info(f"✅ Authenticated user via session token: {user.email}")
                    return (user, None)

                except User.DoesNotExist:
                    logger.warning(f"User not found in session: {user_email}")
                    return None

            except Session.DoesNotExist:
                logger.warning(f"Session not found: {session_uuid}")
                return None

        except ValueError:
            # Invalid auth header format
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None


class SessionOrTokenAuthentication(authentication.BaseAuthentication):
    """
    Authentication that tries both session tokens and Django sessions.
    Falls back to session authentication if token auth fails.
    """

    def authenticate(self, request):
        """
        Try session token authentication first, then fall back to session auth.
        """
        # Try custom session token auth first
        auth_result = SessionTokenAuthentication().authenticate(request)
        if auth_result:
            return auth_result

        # Fall back to Django's session authentication
        return authentication.SessionAuthentication().authenticate(request)
