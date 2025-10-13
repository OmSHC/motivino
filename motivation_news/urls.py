"""
URL configuration for motivation_news project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import homepage, api_docs

urlpatterns = [
    path('', homepage, name='homepage'),
    path('api/', api_docs, name='api-docs'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/users/', include('apps.users.urls')),
    path('api/content/', include('apps.content.urls')),
    path('api/core/', include('apps.core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
