from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from account.permissions import IsStaffMember
from .serializers import *
from .models import *


class CategoriesAllView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    serializer_class = VideoCategorySerializer
    queryset = VideoCategory.objects.all()


class CategoriesNewView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsStaffMember, )
    serializer_class = VideoCategorySerializer
    queryset = VideoCategory.objects.all()


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (AllowAny, )
    serializer_class = VideoCategorySerializer

    def get_queryset(self):
        return VideoCategory.objects.filter(pk=self.kwargs['pk'])

    # Allows anyone to view the category, but only a staff member can modify it
    def check_permissions(self, request):
        super(CategoryRetrieveUpdateDestroyView, self).check_permissions(request)
        permissions = (IsAuthenticated, IsStaffMember)
        if request.method != 'GET':
            for permission in permissions:
                if not permission().has_permission(request, self):
                    self.permission_denied(request)


# Videos
class VideosAllView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VideoSerializer
    queryset = Video.objects.all()


class VideosNewView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsStaffMember, )
    serializer_class = VideoSerializer
    queryset = Video.objects.all()


class VideoUpdateOrDeleteView(generics.DestroyAPIView, generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsStaffMember, )
    serializer_class = VideoSerializer

    def get_queryset(self):
        return Video.objects.filter(pk=self.kwargs['pk'])
