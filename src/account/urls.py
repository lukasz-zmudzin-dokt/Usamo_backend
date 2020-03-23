from django.urls import path
from django.conf.urls import include, url
from .views import *


urlpatterns = [
    path('register/', DefaultAccountRegistrationView.as_view(), name='register'),
    path('register/employer/', EmployerRegistrationView.as_view()),
    path('register/staff/', StaffRegistrationView.as_view()),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('data/', DataView.as_view(), name='data'),
    path('admin/list/', UserListView.as_view(), name='user_list'),
    url(r'^password_reset/',
        include('django_rest_passwordreset.urls', namespace='password_reset')),
]
