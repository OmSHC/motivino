"""
URL configuration for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.api_docs, name='api-docs'),
    path('generate-content/', views.trigger_content_generation, name='generate-content'),
    path('generate-grade-content/', views.trigger_grade_content_generation, name='generate-grade-content'),
    path('generate-quote/', views.trigger_quote_generation, name='generate-quote'),
]
