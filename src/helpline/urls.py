from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.PhoneContactCreateView.as_view()),
    path('contact/<int:contact_id>/', views.PhoneContactView.as_view()),
    path('contacts/', views.PhoneContactListView.as_view())
]