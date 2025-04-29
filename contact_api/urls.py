# contact_api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.contact_api_view, name='contact_api'),
]