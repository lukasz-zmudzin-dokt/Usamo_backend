from django.urls import path

from . import views

urlpatterns = [
    path('blogpost/', views.BlogPostCreateView.as_view()),
    path('blogpost/<int:id>', views.BlogPostView.as_view()),
]
