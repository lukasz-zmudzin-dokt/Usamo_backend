from django_filters import rest_framework as filters
from .models import *


class UserListFilter(filters.FilterSet):
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    date_joined = filters.DateFromToRangeFilter(field_name='date_joined')
    last_login = filters.DateFromToRangeFilter(field_name='last_login')

    class Meta:
        model = Account
        fields = ['id', 'status', 'type', 'username',
                  'email', 'date_joined', 'last_login']


class AbstractTypeListFilter(filters.FilterSet):
    id = filters.UUIDFilter(field_name='id', lookup_expr='icontains')
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    first_name = filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    date_joined = filters.DateFromToRangeFilter(field_name='user__date_joined')
    last_login = filters.DateFromToRangeFilter(field_name='user__last_login')
    status = filters.NumberFilter(field_name='status', lookup_expr='icontains')
    type = filters.NumberFilter(field_name='type', lookup_expr='icontains')


class DefaultAccountListFilter(AbstractTypeListFilter):
    phone_number = filters.CharFilter(
        field_name='account__phone_number', lookup_expr='icontains')
    facility_name = filters.CharFilter(
        field_name='account__facility_name', lookup_expr='icontains')
    facility_address = filters.CharFilter(
        field_name='account__facility_adress', lookup_expr='icontains')

    class Meta:
        model = Account
        fields = ['id', 'status', 'username', 'first_name', 'last_name', 'email',
                  'phone_number', 'facility_name', 'facility_address', 
                  'date_joined', 'last_login']


class EmployerListFilter(AbstractTypeListFilter):
    phone_number = filters.CharFilter(
        field_name='employer_account__phone_number', lookup_expr='icontains')
    company_name = filters.CharFilter(
        field_name='employer_account__company_name', lookup_expr='icontains')
    company_address = filters.CharFilter(
        field_name='employer_account__company_adress', lookup_expr='icontains')
    nip = filters.CharFilter(field_name='nip', lookup_expr='icontains')

    class Meta:
        model = Account
        fields = ['id', 'status', 'username', 'first_name', 'last_name', 'email', 'phone_number',
                  'company_name', 'company_address', 'nip', 'date_joined', 'last_login']


class StaffListFilter(AbstractTypeListFilter):
    group_type = filters.CharFilter(
        field_name='staff_account__group_type', lookup_expr='icontains')

    class Meta:
        model = Account
        fields = ['id', 'username', 'first_name', 'last_name', 'group_type',
                  'email', 'date_joined', 'last_login']
