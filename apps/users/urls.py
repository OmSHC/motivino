"""
URL configuration for users app.
"""
from django.urls import path
from . import views, oauth_views, auth_views

app_name = 'users'

urlpatterns = [
    path('me/', views.get_current_user, name='current-user'),
    path('me/update/', views.update_user_profile, name='update-user'),
    path('track-visit/', views.track_visit, name='track-visit'),
    
    # Email/Password Authentication
    path('signup/', auth_views.signup, name='signup'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    
    # OAuth2 endpoints
    path('oauth/google/callback/', oauth_views.google_oauth_callback, name='google-oauth-callback'),
    path('oauth/google/url/', oauth_views.google_oauth_url, name='google-oauth-url'),
    path('demo/login/', oauth_views.demo_login, name='demo-login'),
]
