from django.contrib.auth.models import Group
from django_filters import rest_framework as filters
from drf_yasg.inspectors import CoreAPICompatInspector, NotHandled
from .models import *
from rest_framework.filters import OrderingFilter


class BlogPostListOrderingFilter(OrderingFilter):
    ordering_description = "umożliwia sortowanie po: 'date_created'"        


class BlogPostListFilter(filters.FilterSet):
    date_created = filters.DateFromToRangeFilter(field_name='date_created')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    author = filters.UUIDFilter(field_name='author__user__id')
    category = filters.CharFilter(field_name='category__name')
    tag = filters.CharFilter(field_name='tags', method='filter_tag')
    
    def filter_tag(self, queryset, name, value):
        tag = BlogPostTag.objects.get(name=value)
        return queryset.filter(tags__in=[tag])

    class Meta:
        model = BlogPost
        fields = ['author', 'title', 'category', 'tag', 'date_created']


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
   def get_filter_parameters(self, filter_backend):
      if isinstance(filter_backend, filters.DjangoFilterBackend):
         result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
         for param in result:
            if not param.get('description', ''):
               param.description = "Filter the returned list by {field_name}".format(field_name=param.name)

         return result

      return NotHandled