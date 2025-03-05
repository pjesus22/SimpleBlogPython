from django.core.signals import post_save
from django.db import models
from django.dispatch import receiver

from apps.utils.base_model import BaseModel

from .posts import Post


class PostStatistics(BaseModel):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, primary_key=True)
    share_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)


@receiver(post_save, sender=Post)
def create_post_statistics(sender, instance, created, **kwargs):
    if created:
        PostStatistics.objects.create(post=instance)
