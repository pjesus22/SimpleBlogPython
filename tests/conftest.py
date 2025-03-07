import shutil
from pathlib import Path

import pytest
from django.conf import settings
from pytest_factoryboy import register

from .factories import (
    AdminFactory,
    AuthorFactory,
    AuthorProfileFactory,
    CategoryFactory,
    MediaFileFactory,
    PostFactory,
    PostStatisticsFactory,
    SocialAccountFactory,
    TagFactory,
)

register(CategoryFactory)
register(PostFactory)
register(PostStatisticsFactory)
register(TagFactory)
register(MediaFileFactory)
register(AdminFactory)
register(AuthorFactory)
register(AuthorProfileFactory)
register(SocialAccountFactory)


@pytest.fixture
def clean_media_dir():
    media_dir = Path(settings.MEDIA_ROOT)

    yield

    if media_dir.exists():
        for item in media_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                print(f'Error removing file: {e}')
