"""
Views for core app.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from .tasks import generate_daily_content, generate_content_for_grade, generate_daily_quote

User = get_user_model()


def homepage(request):
    """
    Homepage view with beautiful HTML template.
    """
    return render(request, 'homepage.html')


def api_docs(request):
    """
    API documentation endpoint.
    """
    return JsonResponse({
        'title': 'Interactive Student Motivation News API',
        'version': '1.0.0',
        'base_url': request.build_absolute_uri('/api/'),
        'authentication': 'OAuth2 (Google)',
        'endpoints': {
            'content': {
                'list': 'GET /api/content/',
                'detail': 'GET /api/content/{id}/',
                'quote': 'GET /api/content/quote/',
                'bookmark': 'POST /api/content/{id}/bookmark/',
                'bookmarks': 'GET /api/content/bookmarks/',
                'admin_list': 'GET /api/content/admin/',
                'admin_create': 'POST /api/content/admin/create/',
                'admin_update': 'PUT /api/content/admin/{id}/update/',
                'admin_delete': 'DELETE /api/content/admin/{id}/delete/'
            },
            'users': {
                'me': 'GET /api/users/me/',
                'update': 'PUT /api/users/me/update/',
                'track_visit': 'POST /api/users/track-visit/'
            },
            'core': {
                'generate_content': 'POST /api/core/generate-content/',
                'generate_grade_content': 'POST /api/core/generate-grade-content/',
                'generate_quote': 'POST /api/core/generate-quote/'
            }
        },
        'sample_requests': {
            'get_content': 'curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/content/',
            'get_quote': 'curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/content/quote/',
            'get_user': 'curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/users/me/'
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_content_generation(request):
    """
    Manually trigger content generation (admin only).
    """
    if not request.user.is_admin():
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Trigger async task
    task = generate_daily_content.delay()
    
    return Response({
        'message': 'Content generation started',
        'task_id': task.id
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_grade_content_generation(request):
    """
    Manually trigger content generation for specific grade (admin only).
    """
    if not request.user.is_admin():
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    grade = request.data.get('grade')
    count = request.data.get('count', 3)
    
    if not grade or not isinstance(grade, int) or grade < 1 or grade > 12:
        return Response(
            {'error': 'Valid grade (1-12) required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Trigger async task
    task = generate_content_for_grade.delay(grade, count)
    
    return Response({
        'message': f'Content generation for grade {grade} started',
        'task_id': task.id
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_quote_generation(request):
    """
    Manually trigger daily quote generation (admin only).
    """
    if not request.user.is_admin():
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Trigger async task
    task = generate_daily_quote.delay()
    
    return Response({
        'message': 'Daily quote generation started',
        'task_id': task.id
    })