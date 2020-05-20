from collections import namedtuple

from django_filters import rest_framework as filters
from drf_yasg.inspectors import CoreAPICompatInspector, NotHandled
from rest_framework.filters import OrderingFilter
from django.db.models import Count
from .models import CV
import re

CustomOrderingParams = namedtuple('CustomOrderingParams', ['related', 'annotate'])


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
   def get_filter_parameters(self, filter_backend):
      if isinstance(filter_backend, filters.DjangoFilterBackend):
         result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
         for param in result:
            if not param.get('description', ''):
               param.description = "Filter the returned list by {field_name}".format(field_name=param.name)

         return result

      return NotHandled


class CvOrderingFilter(OrderingFilter):
    ordering_item_regex = re.compile(r'(-)?(.*)')
    ordering_description = "ordering by: first_name, last_name, email, languages_count, date_created, has_picture"
    custom_fields_dict = {
        'first_name': CustomOrderingParams('basic_info', None),
        'last_name': CustomOrderingParams('basic_info', None),
        'email': CustomOrderingParams('basic_info', None),
        'languages_count': CustomOrderingParams(None, Count('languages'))
    }

    def filter_queryset(self, request, queryset, view):
        def get_ordering_item(item):
            match = self.ordering_item_regex.match(item)
            item_name = match[2]
            if item_name in self.custom_fields_dict:
                related, annotate = self.custom_fields_dict[item_name]
                if annotate:
                    nonlocal queryset
                    queryset = queryset.annotate(**{item_name: annotate})
                if related:
                    direction_str = '' if match[1] is None else match[1]
                    return f'{direction_str}{related}__{item_name}'
                return item
            else:
                return item

        ordering = self.get_ordering(request, queryset, view)
        if ordering:
            custom_ordering = [get_ordering_item(item) for item in ordering]
            return queryset.order_by(*custom_ordering)

        return queryset


class CVListFilter(filters.FilterSet):
    first_name = filters.CharFilter(field_name='basic_info__first_name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='basic_info__last_name', lookup_expr='icontains')
    email = filters.CharFilter(field_name='basic_info__email', lookup_expr='icontains')
    date_posted = filters.DateFromToRangeFilter(field_name='date_posted')
    has_picture = filters.BooleanFilter(field_name='has_picture')
    was_reviewed = filters.BooleanFilter(field_name='was_reviewed')

    class Meta:
        model = CV
        fields = ['first_name', 'last_name', 'email', 'date_created', 'has_picture', 'was_reviewed']
