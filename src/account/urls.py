from django.urls import path
from django.conf.urls import include, url
from .views import *


urlpatterns = [
    path('register/', DefaultAccountRegistrationView.as_view(), name='register'),
    path('register/employer/', EmployerRegistrationView.as_view()),
    path('register/staff/', StaffRegistrationView.as_view()),
    url(r'login/', LoginView.as_view(), name='knox_login'),
    url(r'logout/', LogoutView.as_view(), name='knox_logout'),
    url(r'logout_all/', LogoutAllView.as_view(), name='knox_logout_all'),
    path('data/', DataView.as_view(), name='data'),
    path('status/', UserStatusView.as_view(), name='user_status'),
    path('edit/', AccountEditView.as_view(), name='account_edit'),
    url(r'^admin/user_list/all/$',
        AdminAllAccountsListView.as_view(), name='user_list_all'),
    url(r'^admin/user_list/employers/$',
        AdminEmployerListView.as_view(), name='user_list_employers'),
    url(r'^admin/user_list/default_accounts/$',
        AdminDefaultAccountsListView.as_view(), name='user_list_default_accounts'),
    url(r'^admin/user_list/staff/$',
        AdminStaffListView.as_view(), name='user_list_staff'),
    path('admin/user_details/<uuid:pk>/',
         AdminUserDetailView.as_view(), name='user_data_admin'),
    path('admin/user_admission/<uuid:user_id>/',
         AdminUserAdmissionView.as_view(), name='admit_user_view'),
    path('admin/user_rejection/<uuid:user_id>/',
         AdminUserRejectionView.as_view(), name='reject_user_view'),
    path('admin/user_block/<uuid:user_id>/',
         AdminUserBlockView.as_view(), name='block_user_view'),
    path('admin/user_edit/<uuid:user_id>/',
         AdminAccountEditView.as_view(), name='edit_user_view'),

    url(r'^password_reset/',
        include('django_rest_passwordreset.urls', namespace='password_reset')),
]
