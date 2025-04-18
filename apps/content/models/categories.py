from django.db import models
from django.utils.text import slugify

from apps.utils.base_model import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=50, unique=True, null=False)
    description = models.TextField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=51, unique=True, null=False)

    def __str__(self):
        return self.name

    def full_clean(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.name):
            self.slug = slugify(self.name)
        super().full_clean(*args, **kwargs)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
