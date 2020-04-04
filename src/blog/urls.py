from django.urls import path

from . import views

urlpatterns = [
    path('blogpost/', views.BlogPostCreateView.as_view()),
    path('blogpost/<int:id>', views.BlogPostView.as_view()),
    path('blogposts', views.BlogPostListView.as_view()),
    path('categories', views.BlogPostCategoryListView.as_view()),
    path('tags', views.BlogPostTagListView.as_view())
]
