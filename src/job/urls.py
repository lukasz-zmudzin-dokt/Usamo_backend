from django.urls import path

from . import views

urlpatterns = [
    path('job-offer/<int:offer_id>', views.JobOfferView.as_view()),
    path('job-offer/', views.JobOfferCreateView.as_view()),
    path('job-offers/', views.JobOfferListView.as_view()),
    path('employer/offer-interested/<int:offer_id>', views.JobOfferInterestedUsersView.as_view()),
    path('employer/job-offers/', views.EmployerJobOffersView.as_view()),
]
