from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import create_blog_attachment_file_path, create_blog_header_file_path, create_category_header_file_path
import re
import os
import uuid
from account.models import StaffAccount, DefaultAccount, Account


def clean_html(string):
    cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    return re.sub(cleaner, '', string)


class BlogPostTag(models.Model):
    name = models.CharField(max_length=60, verbose_name='nazwa')


class BlogPostCategory(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name='nazwa')
    header = models.ImageField(upload_to=create_category_header_file_path, null=True, verbose_name='nagłówek')

    class Meta:
        verbose_name = 'kategoria'

    @property
    def header_url(self):
        return self.header.url if self.header.name else None

    def delete_header_if_exists(self, *args, **kwargs) -> bool:
        if self.header.name:
            storage, path = self.header.storage, self.header.path
            self.header.delete()
            storage.delete(path)
        return self.header.name is None


class BlogPostReservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)


class BlogPost(models.Model):
    id = models.OneToOneField(BlogPostReservation, primary_key=True, related_name='blog_post', on_delete=models.CASCADE)
    author = models.ForeignKey(StaffAccount, null=True, on_delete=models.SET_NULL, verbose_name='autor')
    category = models.ForeignKey(BlogPostCategory, on_delete=models.CASCADE, verbose_name='kategoria')
    tags = models.ManyToManyField(BlogPostTag, blank=True, verbose_name='tagi')
    content = models.TextField(verbose_name='treść')
    title = models.CharField(max_length=120, blank=False, null=False, verbose_name='tytuł')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='data stworzenia')
    date_modified = models.DateTimeField(auto_now=True, verbose_name='data ostatniej modyfikacji')
    _summary = models.TextField(null=True)

    class Meta:
        verbose_name = 'post'

    @property
    def summary(self):
        content = clean_html(self.content)
        return content[:300].rstrip() + '...'


class BlogPostHeader(models.Model):
    file = models.ImageField(upload_to=create_blog_header_file_path, verbose_name='plik')
    blog_post = models.OneToOneField(BlogPost, on_delete=models.CASCADE, verbose_name='post')

    class Meta:
        verbose_name = 'nagłówek posta'

    def delete(self, **kwargs):
        self.file.delete()
        self.blog_post.header = None
        super().delete(**kwargs)


class BlogPostAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ImageField(upload_to=create_blog_attachment_file_path, verbose_name='plik')
    blog_post = models.ForeignKey(BlogPostReservation, on_delete=models.CASCADE, verbose_name='post')

    class Meta:
        verbose_name = 'załącznik'

    def delete(self, **kwargs):
        self.file.delete()
        super().delete(**kwargs)


class BlogPostComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, verbose_name='autor')
    content = models.TextField(verbose_name='treść')
    blog_post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE, verbose_name='post')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='data utworzenia')

    class Meta:
        verbose_name = 'komentarz'


@receiver(models.signals.post_delete, sender=BlogPostAttachment)
def delete_attachment_file(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.post_delete, sender=BlogPostHeader)
def delete_header_file(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=BlogPostHeader)
def delete_previous_header_file(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
