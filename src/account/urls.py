from django.urls import path, include
from .views import RegistationView


urlpatterns = [
    path('register/', RegistationView.as_view())
]