from .models import Video
from django_filters import rest_framework as filters


class VideoFilter(filters.FilterSet):
    class Meta:
        model = Video
        fields = ('category', )
