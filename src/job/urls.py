from django.urls import path

from . import views

urlpatterns = [
    # job offers
    path('job-offer/<uuid:offer_id>/', views.JobOfferView.as_view()),
    path('job-offer/', views.JobOfferCreateView.as_view()),
    path('job-offers/', views.JobOfferListView.as_view()),
    path('offer-interested/<uuid:offer_id>/',
         views.JobOfferInterestedUsersView.as_view()),
    # job offers for employers
    path('employer/offer-interested/<uuid:offer_id>/',
         views.EmployerJobOfferInterestedUsersView.as_view()),
    path('employer/job-offers/', views.EmployerJobOffersView.as_view()),
    # enums
    path('enums/voivodeships/', views.VoivodeshipsEnumView.as_view())
]
