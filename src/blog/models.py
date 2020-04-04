from django.db import models
from .utils import create_blog_attachment_file_path

from account.models import StaffAccount, DefaultAccount, Account


def set_summary(content):
    if len(content) < 100:
        return content
    else:
        return content[:100].rstrip() + '...'


class BlogPostTag(models.Model):
    name = models.CharField(max_length=60)


class BlogPostCategory(models.Model):
    name = models.CharField(max_length=60)


class BlogPost(models.Model):
    author = models.ForeignKey(StaffAccount, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(BlogPostCategory, on_delete=models.CASCADE)
    tags = models.ManyToManyField(BlogPostTag, blank=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    summary = models.TextField(null=True)

    def save(self, *args, **kwargs):
        if self.summary is None:
            self.summary = set_summary(self.content)
        super().save()


class BlogPostAttachment(models.Model):
    file = models.FileField(upload_to=create_blog_attachment_file_path, null=True, blank=True)
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)


class BlogPostComment(models.Model):
    author = models.ForeignKey(Account, null=True, on_delete=models.CASCADE)
    content = models.TextField()
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
