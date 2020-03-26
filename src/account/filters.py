from django_filters import rest_framework as filters
from .models import Account


class UserListFilter(filters.FilterSet):
    username = filters.CharFilter(
        field_name='username', lookup_expr='icontains')
    email = filters.CharFilter(
        field_name='email', lookup_expr='icontains')
    date_joined = filters.DateFromToRangeFilter(field_name='date_joined')
    last_login = filters.DateFromToRangeFilter(field_name='last_login')

    class Meta:
        model = Account
        fields = ['status', 'type', 'username',
                  'email', 'date_joined', 'last_login']


class EmployerListFilter(filters.FilterSet):
    username = filters.CharFilter(
        field_name='username', lookup_expr='icontains')
    email = filters.CharFilter(
        field_name='email', lookup_expr='icontains')
    date_joined = filters.DateFromToRangeFilter(field_name='date_joined')
    last_login = filters.DateFromToRangeFilter(field_name='last_login')

    class Meta:
        model = Account
        fields = ['status', 'type', 'username',
                  'email', 'date_joined', 'last_login']
