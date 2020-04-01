from django.utils import timezone
from rest_framework import serializers

from account.serializers import StaffAccountSerializer
from .models import *


class BlogPostTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostTag
        fields = ['name']

    def to_internal_value(self, data):
        formatted_data = {'name': data}
        return super().to_internal_value(formatted_data)


class BlogPostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostCategory
        fields = ['name']

    def to_internal_value(self, data):
        formatted_data = {'name': data}
        return super().to_internal_value(formatted_data)


class BlogPostSerializer(serializers.ModelSerializer):
    category = BlogPostTagSerializer()
    tags = BlogPostTagSerializer(many=True)
    author = StaffAccountSerializer(source='author.user', required=False)

    class Meta:
        model = BlogPost
        fields = ['category', 'tags', 'content', 'date_created', 'author']
        read_only_fields = ['date_created']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['category'] = instance.category.name
        response['tags'] = [tag['name'] for tag in response['tags']]
        return response

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        category, _ = BlogPostCategory.objects.get_or_create(name=category_data['name'])
        blog_post = BlogPost.objects.create(category=category, **validated_data)
        tags_data = validated_data.pop('tags')
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

