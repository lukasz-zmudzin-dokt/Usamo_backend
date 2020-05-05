from django.db import models
from .utils import create_blog_attachment_file_path, create_blog_header_file_path
import re
import uuid
from account.models import StaffAccount, DefaultAccount, Account


def clean_html(string):
    cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    return re.sub(cleaner, '', string)


class BlogPostTag(models.Model):
    name = models.CharField(max_length=60)


class BlogPostCategory(models.Model):
    name = models.CharField(max_length=60)


class BlogPost(models.Model):
    author = models.ForeignKey(StaffAccount, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(BlogPostCategory, on_delete=models.CASCADE)
    tags = models.ManyToManyField(BlogPostTag, blank=True)
    content = models.TextField()
    title = models.TextField(blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    _summary = models.TextField(null=True)

    @property
    def summary(self):
        content = clean_html(self.content)
        return content[:300].rstrip() + '...'


class BlogPostHeader(models.Model):
    file = models.ImageField(upload_to=create_blog_header_file_path)
    blog_post = models.OneToOneField(BlogPost, on_delete=models.CASCADE, null=True)

    def delete(self, **kwargs):
        self.file.delete()
        self.blog_post.header = None
        super().delete(**kwargs)


class BlogPostAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ImageField(upload_to=create_blog_attachment_file_path)
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)

    def delete(self, **kwargs):
        self.file.delete()
        super().delete(**kwargs)

class BlogPostComment(models.Model):
    author = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
    content = models.TextField()
    blog_post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
