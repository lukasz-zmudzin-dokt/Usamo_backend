from django.db import models

# Create your models here.


class VideoCategory(models.Model):
    name = models.CharField(max_length=60)


class Video(models.Model):
    description = models.TextField(blank=True)
    category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, null=True, related_name='videos')
    title = models.CharField(max_length=60)
    url = models.URLField()

    def __str__(self):
        return self.url.__str__()

