from django.urls import path
from .views import *


urlpatterns = [
    path('categories/', CategoriesAllView.as_view()),
    path('category/', CategoriesNewView.as_view()),
    path('category/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view()),
    path('all-videos/', VideosAllView.as_view()),
    path('new-video/', VideosNewView.as_view()),
    path('video/<int:pk>/', VideoRetrieveOrUpdateOrDeleteView.as_view())
]