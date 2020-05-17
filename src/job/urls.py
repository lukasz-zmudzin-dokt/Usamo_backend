from django.urls import path

from . import views

urlpatterns = [
     # job offers
     path('job-offer/', views.JobOfferCreateView.as_view()),
     path('job-offer/<uuid:offer_id>/', views.JobOfferView.as_view()),
     path('job-offer/<uuid:offer_id>/image/', views.JobOfferImageView.as_view()),
     path('job-offers/', views.JobOfferListView.as_view()),
     path('job-offers/application/',
         views.CreateJobOfferApplicationView.as_view()),
     path('job-offers/application/<uuid:offer_id>/',
         views.JobOfferApplicationView.as_view()),
     path('user/application_list/', views.UserApplicationsView.as_view()),
     # job offers for employers
     path('employer/job-offers/', views.EmployerJobOffersView.as_view()),
     path('employer/application_list/<uuid:offer_id>/', views.EmployerApplicationListView.as_view()),
     # job offers for admins
     path('admin/job-offers/unconfirmed/', views.AdminUnconfirmedJobOffersView.as_view()),
     path('admin/confirm/<uuid:offer_id>/', views.AdminConfirmJobOfferView.as_view()),
     # enums
     path('enums/voivodeships/', views.VoivodeshipsEnumView.as_view()),
     path('enums/categories/', views.JobOfferCategoryListView.as_view()),
     path('enums/category/', views.JobOfferCategoryView.as_view()),
     path('enums/types/', views.JobOfferTypesListView.as_view()),
     path('enums/type/', views.JobOfferTypeView.as_view())
]


