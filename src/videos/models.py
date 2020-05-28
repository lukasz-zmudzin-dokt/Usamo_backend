from django.db import models


class VideoCategory(models.Model):
    name = models.CharField(max_length=60)


class Video(models.Model):
    description = models.TextField(blank=True)
    category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, null=True, related_name='videos')
    url = models.URLField()

    def __str__(self):
        return self.url.__str__()

