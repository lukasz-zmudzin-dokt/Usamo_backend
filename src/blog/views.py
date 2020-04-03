from account.models import StaffAccount
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.openapi import Schema, Parameter, IN_PATH
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.serializers import StaffAccountSerializer

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
            "id": Schema(type='integer', default='1')
        }
    )

def sample_blogpost_request(required=True):
    return Schema(
        type='object',
        properties={
            'category': Schema(type='string', default='Kategoria'),
            'tags': Schema(type='array', items=Schema(type='string', default=['Tag1', 'Tag2'])),
            'content': Schema(type='string', format='byte', default='base64-encoded-html-string')
        },
        required=['category', 'tags', 'content'] if required else []
    )

def sample_blogpost_response():
    return Schema(
        type='object',
        properties={
            'category': Schema(type='string', default='Kategoria'),
            'tags': Schema(type='array', items=Schema(type='string', default=['Tag1', 'Tag2'])),
            'content': Schema(type='string', format='byte', default='base64-encoded-html-string'),
            'date_created': Schema(type='string', default="2020-02-20"),
            'author': Schema(
                type='object',
                properties={
                    "email": Schema(type='string', format='email', default='email@example.com'),
                    "first_name": Schema(type='string', default='first_name'),
                    "last_name": Schema(type='string', default='last_name')
                }
            )
        }
    )


class BlogPostCreateView(views.APIView):
    permission_classes = [IsStaffBlogCreator | IsStaffBlogModerator]

    @swagger_auto_schema(
        request_body=sample_blogpost_request(),
        responses={
            200: sample_blogpostid_response(),
            403: 'Forbidden - no permissions',
            400: 'No instance with given id'
        }
    )
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

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('id', IN_PATH, type='integer')
        ],
        responses={
            200: sample_blogpost_response(),
            400: 'No instance with given id'
        }
    )
    def get(self, request, id):
        try:
            blog_post = BlogPost.objects.get(pk=id)
            serializer = BlogPostSerializer(blog_post)
            return Response(serializer.data, status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return ErrorResponse(f"No instance with id: {id}", status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('id', IN_PATH, type='integer')
        ],
        request_body=sample_blogpost_request(required=False),
        responses={
            200: sample_blogpostid_response(),
            403: 'Forbidden - no permissions',
            400: 'No instance with given id'
        }
    )
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

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('id', IN_PATH, type='integer')
        ],
        responses={
            200: "OK",
            403: 'Forbidden - no permissions',
            400: 'No instance with given id'
        }
    )
    def delete(self, request, id):
        try:
            instance = BlogPost.objects.get(pk=id)
            instance.delete()
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return ErrorResponse(f"No instance with id: {id}", status.HTTP_400_BAD_REQUEST)
