from django_filters import rest_framework as filters
from drf_yasg.inspectors import CoreAPICompatInspector, NotHandled
from account.models import Account


class ContactListFilter(filters.FilterSet):
    first_name = filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='first_name', lookup_expr='icontains')

    class Meta:
        model = Account
        fields = ['first_name', 'last_name']


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
   def get_filter_parameters(self, filter_backend):
      if isinstance(filter_backend, filters.DjangoFilterBackend):
         result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
         for param in result:
            if not param.get('description', ''):
               param.description = "Filter the returned list by {field_name}".format(field_name=param.name)

         return result

      return NotHandled