from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import *
from .models import *


class CategoriesAllView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    serializer_class = VideoCategorySerializer
    queryset = VideoCategory.objects.all()


class CategoriesNewView(generics.CreateAPIView):
    permission_classes = (AllowAny, )
    serializer_class = VideoCategorySerializer
    queryset = VideoCategory.objects.all()


class CategoryUpdateOrDeleteOrListView(generics.DestroyAPIView, generics.UpdateAPIView, generics.ListAPIView):
    permission_classes = (AllowAny, )
    serializer_class = VideoCategorySerializer

    def get_queryset(self):
        return VideoCategory.objects.filter(pk=self.kwargs['pk'])


# Videos

class VideosAllView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VideoSerializer
    queryset = Video.objects.all()


class VideosNewView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VideoSerializer
    queryset = Video.objects.all()


class VideoUpdateOrDeleteView(generics.DestroyAPIView, generics.UpdateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VideoSerializer

    def get_queryset(self):
        return Video.objects.filter(pk=self.kwargs['pk'])
