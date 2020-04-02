from account.models import StaffAccount
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.openapi import Schema
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.permissions import IsStaffBlogCreator, IsStaffBlogModerator

from .permissions import *
from .serializers import *


class ErrorResponse(Response):
    def __init__(self, error_message, status_code):
        super().__init__(data={"error": error_message}, status=status_code)


def sample_error_response(error_message):
    return Schema(
        type='object',
        properties={
            "error": Schema(type='string', default=error_message)
        }
    )


class BlogPostIdResponse(Response):
    def __init__(self, id):
        super().__init__(data={"id": id}, status=status.HTTP_200_OK)


def sample_blogpostid_response():
    return Schema(
        type='object',
        properties={
            "id": Schema(type='int', default='1')
        }
    )


class BlogPostCreateView(views.APIView):
    permission_classes = [IsStaffBlogCreator | IsStaffBlogModerator]

    def post(self, request):
        try:
            author = StaffAccount.objects.get(user_id=request.user.id)
            serializer = BlogPostSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.create(serializer.validated_data)
                instance.author_id = author.id
                instance.save()
                return BlogPostIdResponse(instance.id)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return ErrorResponse("No user or user is not staff member", status.HTTP_403_FORBIDDEN)


class BlogPostView(views.APIView):
    permission_classes = [GetRequestPublicPermission |
                          IsStaffBlogModerator | IsStaffBlogCreator]

    def get(self, request, id):
        try:
            blog_post = BlogPost.objects.get(pk=id)
            serializer = BlogPostSerializer(blog_post)
            return Response(serializer.data, status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return ErrorResponse(f"No instance with id: {id}", status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        try:
            instance = BlogPost.objects.get(pk=id)
            serializer = BlogPostSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return BlogPostIdResponse(instance.id)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return ErrorResponse(f"No instance with id: {id}", status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            instance = BlogPost.objects.get(pk=id)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return ErrorResponse(f"No instance with id: {id}", status.HTTP_400_BAD_REQUEST)
