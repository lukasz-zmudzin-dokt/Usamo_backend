from django.utils import timezone
from rest_framework import serializers

from account.models import StaffAccount, Account

from .models import *


class BlogPostTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostTag
        fields = ['name']

    def to_internal_value(self, data):
        formatted_data = {'name': data}
        return super().to_internal_value(formatted_data)

    def to_representation(self, instance):
        return instance.name


class BlogPostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostCategory
        fields = ['name']

    def to_internal_value(self, data):
        formatted_data = {'name': data}
        return super().to_internal_value(formatted_data)

    def to_representation(self, instance):
        return instance.name


class BlogAuthorSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    id = serializers.UUIDField(source='user.id', read_only=True)

    class Meta:
        model = StaffAccount
        fields = ['email', 'first_name', 'last_name', 'id']


class CommentAuthorSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = Account
        fields = ['email', 'first_name', 'last_name', 'id']


class BlogPostCommentSerializer(serializers.ModelSerializer):
    author = CommentAuthorSerializer(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = BlogPostComment
        fields = ['id', 'blog_post', 'author', 'content', 'date_created']
        read_only_fields = ['id', 'date_created']
        extra_kwargs = {
            'blog_post': {'write_only': True}
        }

    def create(self, validated_data):
        return BlogPostComment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance


class BlogPostSerializer(serializers.ModelSerializer):
    category = BlogPostTagSerializer()
    tags = BlogPostTagSerializer(many=True)
    author = BlogAuthorSerializer(read_only=True)
    comments = BlogPostCommentSerializer(many=True, read_only=True)
    summary = serializers.CharField(required=False, read_only=True)
    header = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'category', 'tags', 'content', 'date_created', 'author', 'comments', 'summary', 'title', 'header']
        read_only_fields = ['id', 'date_created', 'author', 'comments']

    def get_header(self, obj):
        header = BlogPostHeader.objects.filter(blog_post_id=obj.id).first()
        return header.file.url if header else ""

    def to_representation(self, instance):
        response = super().to_representation(instance)
        return response

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        category_data = validated_data.pop('category')
        category, _ = BlogPostCategory.objects.get_or_create(name=category_data['name'])
        blog_post = BlogPost.objects.create(category=category, **validated_data)
        for tag_data in tags_data:
            tag, _ = BlogPostTag.objects.get_or_create(name=tag_data['name'])
            blog_post.tags.add(tag)
        return blog_post

    def update(self, instance, validated_data):
        if 'category' in validated_data:
            category_data = validated_data['category']
            category, _ = BlogPostCategory.objects.get_or_create(name=category_data['name'])
            instance.category = category

        if 'tags' in validated_data:
            instance.tags.clear()
            for tag_data in validated_data['tags']:
                tag, _ = BlogPostTag.objects.get_or_create(name=tag_data['name'])
                instance.tags.add(tag)

        if 'content' in validated_data:
            instance.content = validated_data.get('content', instance.content)

        instance.date_modified = timezone.now()
        instance.save()
        return instance


class BlogPostListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)
    category = BlogPostTagSerializer(read_only=True)
    tags = BlogPostTagSerializer(many=True, read_only=True)
    author = BlogAuthorSerializer(read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'author', 'category', 'tags', 'summary']


class BlogPostHeaderSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogPostHeader
        fields = '__all__'


class BlogPostAttachmentSerializer(serializers.ModelSerializer):
    attachment_url = serializers.CharField(source='file.url', read_only=True)

    class Meta:
        model = BlogPostAttachment
        fields = ['id', 'blog_post', 'file', 'attachment_url']
        extra_kwargs = {
            'file': {'write_only': True},
            'id': {'required': False}
        }


