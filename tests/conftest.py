import shutil
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
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


@pytest.fixture
def csrf_client():
    client = Client(enforce_csrf_checks=True)
    return client


@pytest.fixture
def logged_admin_client(admin_factory, csrf_client):
    user = admin_factory.create(username='test-admin')
    csrf_client.force_login(user)
    response = csrf_client.get('/api/v1/auth/csrf-token/')
    csrf_token = response.cookies['csrftoken'].value
    csrf_client.defaults['HTTP_X_CSRFTOKEN'] = csrf_token
    return csrf_client


@pytest.fixture
def logged_author_client(author_factory, csrf_client):
    user = author_factory.create(username='test-author')
    csrf_client.force_login(user)
    response = csrf_client.get('/api/v1/auth/csrf-token/')
    csrf_token = response.cookies['csrftoken'].value
    csrf_client.defaults['HTTP_X_CSRFTOKEN'] = csrf_token
    return csrf_client
