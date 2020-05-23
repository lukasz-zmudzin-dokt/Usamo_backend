from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from blog.permissions import IsStaffBlogModerator
from .serializers import *
from .models import *
from django_filters import rest_framework as filters
from .filters import VideoFilter


class BaseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    # Allows anyone to view the content, but only a staff member can modify it
    def check_permissions(self, request):
        super(BaseRetrieveUpdateDestroyView, self).check_permissions(request)
        permissions = (IsAuthenticated, IsStaffBlogModerator)
        if request.method != 'GET':
            for permission in permissions:
                if not permission().has_permission(request, self):
                    self.permission_denied(request)


class CategoriesAllView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    serializer_class = VideoCategorySerializer
    queryset = VideoCategory.objects.all()


class CategoriesNewView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsStaffBlogModerator, )
    serializer_class = VideoCategorySerializer
    queryset = VideoCategory.objects.all()


class CategoryRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    permission_classes = (AllowAny, )
    serializer_class = VideoCategorySerializer

    def get_queryset(self):
        return VideoCategory.objects.filter(pk=self.kwargs['pk'])


# Videos
class VideosAllView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VideoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = VideoFilter
    queryset = Video.objects.all()


class VideosNewView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsStaffBlogModerator, )
    serializer_class = VideoSerializer
    queryset = Video.objects.all()


class VideoRetrieveOrUpdateOrDeleteView(BaseRetrieveUpdateDestroyView):
    permission_classes = (AllowAny, )
    serializer_class = VideoSerializer

    def get_queryset(self):
        return Video.objects.filter(pk=self.kwargs['pk'])
