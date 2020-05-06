import os
from django.utils.datastructures import MultiValueDictKeyError
from account.models import StaffAccount, DefaultAccount, Account
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from drf_yasg.openapi import IN_QUERY, IN_FORM
from drf_yasg.openapi import Schema, Parameter, IN_PATH
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from account.account_type import StaffGroupType
from account.permissions import GetRequestPublicPermission
from django.contrib.auth.models import Group
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
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


class BlogPostCommentIdResponse(Response):
    def __init__(self, id):
        super().__init__(data={"id": id}, status=status.HTTP_200_OK)


def sample_blogpostid_response():
    return Schema(
        type='object',
        properties={
            "id": Schema(type='integer', default='1')
        }
    )


def sample_commentid_response():
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
            'content': Schema(type='string', format='byte', default='base64-encoded-html-string'),
            'title': Schema(type='string', default='Title')
        },
        required=['category', 'tags', 'content', 'title'] if required else []
    )


def sample_comment_request(required=True):
    return Schema(
        type='object',
        properties={
            'content': Schema(type='string', format='byte', default='base64-encoded-html-string')
        },
        required=['content'] if required else []
    )


def sample_blogpost_response():
    return Schema(
        type='object',
        properties={
            'id': Schema(type='integer', default="1"),
            'category': Schema(type='string', default='Kategoria'),
            'tags': Schema(type='array', items=Schema(type='string', default=['Tag1', 'Tag2'])),
            'content': Schema(type='string', format='byte', default='base64-encoded-html-string'),
            'title': Schema(type='string', default='Title'),
            'header': Schema(type='string', default='header-url'),
            'date_created': Schema(type='string', default="2020-02-20"),
            'author': Schema(
                type='object',
                properties={
                    "email": Schema(type='string', format='email', default='email@example.com'),
                    "first_name": Schema(type='string', default='first_name'),
                    "last_name": Schema(type='string', default='last_name')
                }
            ),
            'comments': Schema(
                type='array',
                items=Schema(
                    type='object',
                    properties={
                        "id": Schema(type='integer', default="1"),
                        "author": {
                            "email": Schema(type='string', format='email', default='email@example.com'),
                            "first_name": Schema(type='string', default='first_name'),
                            "last_name": Schema(type='string', default='last_name')
                        },
                        "content": Schema(type='string', default='Treść komentarza'),
                        "date_created": Schema(type='string')
                    }
                )
            )
        }
    )


def sample_string_response():
    return Schema(
        type='array',
        items=Schema(type='string')
    )


class BlogPostCreateView(views.APIView):
    permission_classes = [IsAuthenticated, IsStaffBlogCreator]

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
                instance.author = author
                instance.save()
                return BlogPostIdResponse(instance.id)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return ErrorResponse("No user or user is not staff member", status.HTTP_403_FORBIDDEN)


class BlogPostHeaderView(views.APIView):

    permission_classes = (IsAuthenticated, IsStaffBlogCreator | IsStaffBlogModerator)
    parser_classes = (MultiPartParser, )

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('id', IN_PATH, type='integer'),
            Parameter('file', IN_FORM, type='file')
        ],
        responses={
            200: '"message": "Nagłówek został pomyślnie utworzony"',
            400: '"error": "Post o podanym id nie istnieje" / "Nie znaleziono pliku"'
        },
    )
    def post(self, request, id):
        existing_header = BlogPostHeader.objects.filter(blog_post_id=id)
        existing_header.delete()

        blog_post = BlogPost.objects.filter(id=id).first()
        if not blog_post:
            return ErrorResponse('Post o podanym id nie istnieje', status.HTTP_400_BAD_REQUEST)
        
        try:
            data = {'blog_post': blog_post.id, 'file': request.FILES['file']}
        except MultiValueDictKeyError:
            return ErrorResponse('Nie znaleziono pliku. Upewnij się, że został on załączony pod kluczem file',
                status.HTTP_400_BAD_REQUEST)

        serializer = BlogPostHeaderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return ErrorResponse(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        response_data = {"message": "Nagłówek został pomyślnie utworzony"}
        return Response(response_data, status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('id', IN_PATH, type='integer')
        ],
        responses={
            200: '"message": "Nagłówek został pomyślnie usunięty"',
            400: '"error": "Post o danym id nie ma nagłówka"'
        }
    )
    def delete(self, request, id):
        header = BlogPostHeader.objects.filter(blog_post_id=id)
        if not header:
            return ErrorResponse("Post o danym id nie ma nagłówka", status.HTTP_400_BAD_REQUEST)
        header = BlogPostHeader.objects.get(blog_post_id=id)
        header.delete()
        response_data = {"message": "Nagłówek został pomyślnie usunięty"}
        return Response(response_data, status.HTTP_200_OK)


class BlogPostAttachmentUploadView(views.APIView):

    permission_classes = [IsStaffBlogCreator]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('blog_id', IN_PATH, type='integer'),
            Parameter('file', IN_FORM, type='file')
        ],
        responses={
            200: '"attachment_url": url',
            400: '"error": "Post o podanym id nie istnieje" / "Nie znaleziono pliku"'
        },
    )
    def post(self, request, blog_id):
        blog_post = BlogPost.objects.get(pk=blog_id)
        if not blog_post:
            return ErrorResponse('Post o podanym id nie istnieje', status.HTTP_400_BAD_REQUEST)
        
        try:
            data = {'blog_post': blog_post.id, 'file': request.FILES['file']}
        except MultiValueDictKeyError:
            return ErrorResponse('Nie znaleziono pliku. Upewnij się, że został on załączony pod kluczem file',
                status.HTTP_400_BAD_REQUEST)

        serializer = BlogPostAttachmentSerializer(data=data)
        if serializer.is_valid():
            attachment = serializer.save()
        else:
            return ErrorResponse(serializer.errors, status.HTTP_400_BAD_REQUEST)

        response_data = {"attachment_url": attachment.file.url}
        return Response(response_data, status.HTTP_200_OK)


class BlogPostAttachmentDeleteView(views.APIView):

    permission_classes = [IsStaffBlogCreator]

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('attachment_id', IN_PATH, type='string($uuid)')
        ],
        responses={
            200: '"message": "Załącznik o podanym id został usunięty"',
            400: '"error": "Nie znaleziono załącznika o podanym id"'
        }
    )
    def delete(self, request, attachment_id):
        attachment = BlogPostAttachment.objects.get(pk=attachment_id)
        if not attachment:
            return ErrorResponse('Nie znaleziono załącznika o podanym id', status.HTTP_400_BAD_REQUEST)
        attachment.delete()
        response_data = {"message": "Załącznik o podanym id został usunięty"}
        return Response(response_data, status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': BlogPostAttachmentSerializer(many=True),
        '404': "Not found",
    }
))
class BlogPostAttachmentListView(generics.ListAPIView):
    serializer_class = BlogPostAttachmentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        id = self.kwargs['blog_id']
        return BlogPostAttachment.objects.filter(blog_post_id=id)


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


@method_decorator(name='get', decorator=swagger_auto_schema(
        operation_description="Returns list of all categories.",
        responses={
            200: sample_string_response()
        }
    ))
class BlogPostCategoryListView(generics.ListAPIView):
    serializer_class = BlogPostCategorySerializer
    permission_classes = [AllowAny]
    queryset = BlogPostCategory.objects.all()


@method_decorator(name='get', decorator=swagger_auto_schema(
        operation_description="Returns list of all tags.",
        responses={
            200: sample_string_response()
        }
    ))
class BlogPostTagListView(generics.ListAPIView):
    serializer_class = BlogPostTagSerializer
    permission_classes = [AllowAny]
    queryset = BlogPostTag.objects.all()


@method_decorator(name='get', decorator=swagger_auto_schema(
        manual_parameters=[
            Parameter('category', IN_QUERY, type='string'),
            Parameter('tag', IN_QUERY, type='string')
        ],
        operation_description="Returns blog post list. Can be filtered by category and/or tag."
    ))
class BlogPostListView(generics.ListAPIView):
    serializer_class = BlogPostListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = BlogPost.objects.all()
        category = self.request.query_params.get('category', None)
        tag = self.request.query_params.get('tag', None)
        if category is not None:
            queryset = queryset.filter(category__name=category)
        if tag is not None:
            queryset = queryset.filter(tags__name__contains=tag)
        return queryset


class BlogPostCommentCreateView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=sample_comment_request(),
        responses={
            200: sample_commentid_response(),
            403: 'Forbidden - no permissions',
            400: 'No blog_post instance with given id'
        }
    )
    def post(self, request, id):
        try:
            author = Account.objects.get(id=request.user.id)
        except ObjectDoesNotExist:
            return ErrorResponse("No user?", status.HTTP_403_FORBIDDEN)
        try:
            blog_post = BlogPost.objects.get(pk=id)
            request.data["blog_post"] = blog_post.pk
            serializer = BlogPostCommentSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.create(serializer.validated_data)
                instance.author = author
                instance.blog_post = blog_post
                instance.save()
                return BlogPostCommentIdResponse(instance.id)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return ErrorResponse(f"No blog with id: {id}", status.HTTP_400_BAD_REQUEST)


class BlogPostCommentUpdateView(views.APIView):
    permission_classes = [IsUserCommentAuthor | IsStaffBlogModerator]

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('id', IN_PATH, type='integer')
        ],
        responses={
            200: "Comment was successfully deleted",
            403: 'Forbidden - no permissions',
            400: 'No instance with given id'
        }
    )
    def delete(self, request, id):
        try:
            comment = BlogPostComment.objects.get(pk=id)
        except ObjectDoesNotExist:
            return ErrorResponse(f"No comment with id: {id}", status.HTTP_400_BAD_REQUEST)

        if IsUserCommentAuthor().has_object_permission(request, self, comment) or \
                IsStaffBlogModerator().has_object_permission(request, self, comment):
            comment.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return ErrorResponse("You can't delete this comment.", status.HTTP_403_FORBIDDEN)