from django.db import models
from django.utils.text import slugify

from apps.utils.base_model import BaseModel


class Tag(BaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, null=False)

    def __str__(self):
        return self.name

    def clean(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.name):
            self.slug = slugify(self.name)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['pk']
