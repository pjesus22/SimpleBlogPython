from django.db import models
from django.utils.text import slugify

from apps.utils.base_model import BaseModel


class Tag(BaseModel):
    name = models.CharField(max_length=51)
    slug = models.SlugField(max_length=51, unique=True, null=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
