import json

import pytest
from django.urls import reverse

from apps.content.models import Tag


@pytest.fixture
def tag(tag_factory):
    return tag_factory.create(name='test tag')


def test_delete_tag_success(db, logged_admin_client, tag):
    url = reverse('tag-detail', kwargs={'slug': tag.slug})
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 204


def test_delete_tag_not_found(db, logged_admin_client):
    url = reverse('tag-detail', kwargs={'slug': 'non-existing-slug'})
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 404


def test_delete_tag_generic_exception(db, logged_admin_client, override, tag):
    def fake_delete(*args, **kwargs):
        raise Exception('Something went wrong')

    with override(Tag, 'delete', fake_delete):
        response = logged_admin_client.delete(
            path=reverse('tag-detail', kwargs={'slug': tag.slug}),
            data=json.dumps({'name': 'test tag'}),
        )

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
