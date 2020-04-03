from django.urls import path

from . import views

urlpatterns = [
    path('', views.BlogPostCreateView.as_view()),
    path('<int:id>', views.BlogPostView.as_view()),
    path('list', views.BlogPostListView.as_view()),
    path('category/list/', views.BlogPostCategoryListView.as_view())
]
