# contact_api/urls.py

from django.urls import path
from . import views # Import views from the current app directory

urlpatterns = [
    # When someone visits /api/contact/ (the /api/ part is added later), run contact_api_view
    path('contact/', views.contact_api_view, name='contact_api'),
]