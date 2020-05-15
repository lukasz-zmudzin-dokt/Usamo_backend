from django.conf.urls import url
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views
import uuid

urlpatterns = [
    path('generator/', views.CreateCVView.as_view(), name='cv_generator'),
    path('generator/<uuid:cv_id>/', views.CVView.as_view(), name='cv_view'),
    path('data/<uuid:cv_id>/', views.CVDataView.as_view(), name='cv_data'),
    path('picture/<uuid:cv_id>/', views.CVPictureView.as_view(), name='cv_picture'),
    path('feedback/<uuid:cv_id>/', views.CVFeedback.as_view(), name='cv_feedback'),
    path('admin/list/unverified/', views.AdminUnverifiedCVList.as_view(), name='cv_unverified_list'),
    path('admin/list/', views.AdminCVListView.as_view(), name='cv_list'),
    path('user/list/', views.UserCVListView.as_view(), name='user_cv_list'),
    path('admin/feedback/', views.AdminFeedback.as_view(), name='feedback'),
    path('admin/verification/<uuid:cv_id>/', views.AdminCVVerificationView.as_view(), name='cv_verification'),
    path('status/<uuid:cv_id>/', views.CVStatus.as_view(), name='cv_status'),
    path('name/<uuid:cv_id>/', views.UserCVNameView.as_view(), name='cv_name'),
    path('generator/can-post/', views.UserCVAvailabilityView.as_view(), name='cv_generator_can_post'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
