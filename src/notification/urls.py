from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('list/all', views.AllNotifications.as_view()),
    path('list/all/mark-as-read/', views.MarkAllAsRead.as_view()),
    path('list/all/delete/', views.DeleteAll.as_view()),
    path('list/unread', views.UnreadNotifications.as_view()),
    path('count/unread', views.UnreadNotificationsCount.as_view()),
    path('mark-as-read/<int:slug>/', views.MarkAsRead.as_view()),
    path('delete/<int:slug>/', views.Delete.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
