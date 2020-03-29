from django.db import models
from .utils import create_blog_attachment_file_path, create_blog_content_file_path

from account.models import StaffAccount, Account


class BlogPostTag(models.Model):
    name = models.CharField(max_length=60)


class BlogPost(models.Model):
    author = models.ForeignKey(StaffAccount, null=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=60)
    tags = models.ManyToManyField(BlogPostTag, blank=True)
    content = models.FileField(upload_to=create_blog_content_file_path)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class BlogPostAttachment(models.Model):
    file = models.FileField(upload_to=create_blog_attachment_file_path, null=True, blank=True)
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)


class BlogPostComment(models.Model):
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    content = models.TextField()
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)

