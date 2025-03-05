import os

from django.core.exceptions import ValidationError
from django.db import models
from PIL import Image

from apps.utils.base_model import BaseModel


def get_upload_path(instance, filename):
    ext = filename.split('.')[-1].lstrip('.').lower()
    file_type = instance._get_file_type(ext)
    return os.path.join(str(instance.post.author.id), file_type, filename)


class MediaFile(BaseModel):
    class Type(models.TextChoices):
        IMAGE = 'image'
        VIDEO = 'video'
        AUDIO = 'audio'

    valid_extensions = {
        Type.IMAGE: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
        Type.VIDEO: ['mp4', 'webm'],
        Type.AUDIO: ['mp3', 'aac', 'wav', 'ogg'],
    }

    file = models.FileField(upload_to=get_upload_path)
    post = models.ForeignKey(
        'content.Post', on_delete=models.CASCADE, related_name='media_files'
    )
    name = models.CharField(max_length=255)
    type = models.CharField(choices=Type.choices, max_length=10)
    size = models.PositiveIntegerField()
    width = models.PositiveIntegerField(null=True)
    height = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name

    def _get_file_type(self, ext):
        for file_type, extensions in self.valid_extensions.items():
            if ext in extensions:
                return file_type
        raise ValidationError(f'Invalid file type: .{ext} is not allowed.')

    def _extract_image_metadata(self):
        try:
            with Image.open(self.file) as img:
                self.width, self.height = img.size
        except Exception as e:
            raise ValidationError(f'Error extracting image metadata: {e}')

    def save(self, *args, **kwargs):
        if self.file:
            self.name = os.path.basename(self.file.name)
            ext = self.name.split('.')[-1].lstrip('.').lower()
            self.type = self._get_file_type(ext)
            self.size = self.file.size

            if self.type == self.Type.IMAGE:
                self._extract_image_metadata()
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Media File'
        verbose_name_plural = 'Media Files'
