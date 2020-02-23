from django.urls import path

from . import views

urlpatterns = [
    path('offer-get/<int:pk>', views.JobOfferGetView.as_view(), name='offer-get'),
    path('offer-list/', views.JobOfferListView.as_view(), name='offer-list'),
    path('offer-create/', views.JobOfferCreateView.as_view(), name='offer-create'),
    path('offer-edit/', views.JobOfferEditView.as_view(), name='offer-edit'),
    path('offer-interested/<int:offer_id>', views.JobOfferInterestedUsersView.as_view(), name='offer-interested'),
]
