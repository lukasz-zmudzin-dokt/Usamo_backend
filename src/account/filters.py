from django.contrib.auth.models import Group
from django_filters import rest_framework as filters
from drf_yasg.inspectors import CoreAPICompatInspector, NotHandled
from usamo.settings.settings import PASS_RESET_URL
from .models import *
from .account_type import *
from .account_status import *


class UserListFilter(filters.FilterSet):
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    date_joined = filters.DateFromToRangeFilter(field_name='date_joined')
    last_login = filters.DateFromToRangeFilter(field_name='last_login')
    status = filters.ChoiceFilter(choices=STATUS_CHOICES_VERBOSE, method='filter_status')
    type = filters.ChoiceFilter(choices=TYPE_CHOICES_VERBOSE, method='filter_type')

    def filter_status(self, queryset, name, value):
        value = STATUS_TO_INT_MAP[value]
        return queryset.filter(status=value)


    def filter_type(self, queryset, name, value):
        value = TYPE_TO_INT_MAP[value]
        return queryset.filter(type=value)

    class Meta:
        model = Account
        fields = ['status', 'type', 'username',
                  'email', 'date_joined', 'last_login']


class DefaultAccountListFilter(UserListFilter):
    phone_number = filters.CharFilter(
        field_name='account__phone_number', lookup_expr='icontains')
    facility_name = filters.CharFilter(
        field_name='account__facility_name', lookup_expr='icontains')
    city = filters.CharFilter(
        field_name='account__facility_address__city', lookup_expr='icontains')

    class Meta:
        model = Account
        fields = ['id', 'status', 'username', 'email','phone_number', 'facility_name', 'city', 
                    'date_joined', 'last_login']


class EmployerListFilter(UserListFilter):
    phone_number = filters.CharFilter(
        field_name='employer_account__phone_number', lookup_expr='icontains')
    company_name = filters.CharFilter(
        field_name='employer_account__company_name', lookup_expr='icontains')
    city = filters.CharFilter(
        field_name='employer_account__company_address__city', lookup_expr='icontains')
    nip = filters.CharFilter(field_name='employer_account__nip', lookup_expr='icontains')

    class Meta:
        model = Account
        fields = ['id', 'status', 'username', 'email', 'phone_number',
                  'company_name', 'city', 'nip', 'date_joined', 'last_login']


class StaffListFilter(UserListFilter):

    group_type = filters.MultipleChoiceFilter(choices=STAFF_GROUP_CHOICES,
                                              field_name='groups',
                                              method='filter_groups')

    class Meta:
        model = Account
        fields = ['id', 'username', 'group_type','email', 'date_joined', 'last_login']

    def filter_groups(self, queryset, name, values):
        if name != 'groups':
            return queryset.none()
        groups = Group.objects.filter(name__in=values)
        return queryset.filter(groups__in=groups).distinct()


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
   def get_filter_parameters(self, filter_backend):
      if isinstance(filter_backend, filters.DjangoFilterBackend):
         result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
         for param in result:
            if not param.get('description', ''):
               param.description = "Filter the returned list by {field_name}".format(field_name=param.name)

         return result

      return NotHandled