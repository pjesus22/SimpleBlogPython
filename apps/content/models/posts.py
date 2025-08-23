from django.db import models
from django.utils.text import slugify

from apps.utils.base_model import BaseModel

from .categories import Category
from .tags import Tag


class Post(BaseModel):
    class Status(models.TextChoices):
        DRAFT = 'draft'
        PUBLISHED = 'published'
        ARCHIVED = 'archived'
        DELETED = 'deleted'

    author = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='posts'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    title = models.CharField(
        max_length=50,
        blank=False,
        null=False,
    )
    slug = models.SlugField(max_length=50, unique=True, null=False)
    content = models.TextField(
        blank=False,
        null=False,
    )
    status = models.CharField(
        choices=Status.choices,
        max_length=10,
        default=Status.DRAFT,
    )

    def __str__(self):
        return self.title

    def full_clean(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.title):
            self.slug = slugify(self.title)
        super().full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def is_public(self) -> bool:
        return self.status == self.Status.PUBLISHED

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = ('author', 'slug')
