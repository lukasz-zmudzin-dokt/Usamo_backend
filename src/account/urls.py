from django.urls import path
from .views import RegistationView, LogoutView, DataView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('register/', RegistationView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', obtain_auth_token, name='login'),
    path('data/', DataView.as_view(), name='data')
]