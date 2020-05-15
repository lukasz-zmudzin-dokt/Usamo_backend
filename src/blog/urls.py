from django.urls import path

from . import views

urlpatterns = [
    path('blogpost/', views.BlogPostCreateView.as_view()),
    path('blogpost/reservation/', views.BlogPostReservationView.as_view()),
    path('blogpost/<uuid:post_id>/', views.BlogPostView.as_view()),
    path('blogpost/<uuid:post_id>/attachment-list/', views.BlogPostAttachmentListView.as_view()),
    path('blogpost/<uuid:post_id>/attachment-upload/', views.BlogPostAttachmentUploadView.as_view()),
    path('attachments/<uuid:attachment_id>/', views.BlogPostAttachmentDeleteView.as_view()),
    path('blogpost/<uuid:post_id>/header/', views.BlogPostHeaderView.as_view()),
    path('blogposts/', views.BlogPostListView.as_view()),
    path('categories/', views.BlogPostCategoryListView.as_view()),
    path('tags/', views.BlogPostTagListView.as_view()),
    path('<uuid:post_id>/comment/', views.BlogPostCommentCreateView.as_view()),
    path('comment/<uuid:comment_id>/', views.BlogPostCommentUpdateView.as_view()),
]
