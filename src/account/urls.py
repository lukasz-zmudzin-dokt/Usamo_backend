from django.urls import path
from .views import DefaultAccountRegistrationView, LogoutView, DataView, EmployerRegistrationView, StaffRegistrationView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('register/', DefaultAccountRegistrationView.as_view(), name='register'),
    path('register/employer/', EmployerRegistrationView.as_view()),
    path('register/staff/', StaffRegistrationView.as_view()),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', obtain_auth_token, name='login'),
    path('data/', DataView.as_view(), name='data')
]