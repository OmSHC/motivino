"""
URL configuration for content app.
"""
from django.urls import path
from . import views, submission_views

app_name = 'content'

urlpatterns = [
    # Public content endpoints
    path('', views.ContentListView.as_view(), name='content-list'),
    path('<uuid:id>/', views.ContentDetailView.as_view(), name='content-detail'),
    path('quote/', views.get_daily_quote, name='daily-quote'),
    path('<uuid:content_id>/bookmark/', views.toggle_bookmark, name='toggle-bookmark'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmark-list'),
    # Comment endpoints
    path('<uuid:content_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<uuid:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    
    # User submission endpoints
    path('submit-story/', submission_views.submit_story, name='submit-story'),
    path('my-submissions/', submission_views.get_my_submissions, name='my-submissions'),
    
    # Admin endpoints
    path('admin/', views.AdminContentListView.as_view(), name='admin-content-list'),
    path('admin/create/', views.AdminContentCreateView.as_view(), name='admin-content-create'),
    path('admin/<uuid:pk>/update/', views.AdminContentUpdateView.as_view(), name='admin-content-update'),
    path('admin/<uuid:pk>/delete/', views.AdminContentDeleteView.as_view(), name='admin-content-delete'),
    path('admin/pending/', submission_views.get_pending_submissions, name='pending-submissions'),
    path('admin/<uuid:content_id>/approve/', submission_views.approve_submission, name='approve-submission'),
    path('admin/<uuid:content_id>/reject/', submission_views.reject_submission, name='reject-submission'),
    path('resubmit/<uuid:content_id>/', submission_views.resubmit_story, name='resubmit-story'),
]
