from pathlib import Path
from random import choice

import factory
from django.core.files.base import ContentFile

from .content.post import PostFactory


def get_mock_data(path):
    media_path = Path(path)
    if not media_path.exists() or not media_path.is_dir():
        raise FileNotFoundError(f'Media path {path} is invalid or does not exist')
    file_list = [f for f in media_path.iterdir() if f.is_file()]
    if not file_list:
        raise FileNotFoundError(f'No files found in {path}')
    selected_file = choice(file_list)
    with open(selected_file, 'rb') as f:
        content = f.read()
    return ContentFile(content, name=selected_file.name)


class MediaFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'media_files.MediaFile'

    @factory.lazy_attribute
    def file(self):
        return get_mock_data(path='tests/mock_data')

    post = factory.SubFactory(PostFactory)
