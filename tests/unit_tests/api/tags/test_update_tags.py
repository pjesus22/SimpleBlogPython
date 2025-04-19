import json

import pytest
from django.urls import reverse

from apps.content.models import Tag

pytestmark = pytest.mark.django_db


@pytest.fixture
def tag(tag_factory):
    return tag_factory.create(name='test tag')


def test_patch_tag_success(logged_admin_client, tag):
    url = reverse('tag-detail', kwargs={'slug': 'test-tag'})
    payload = {'name': 'updated name'}
    response = logged_admin_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['data']['attributes']['name'] == 'updated name'


def test_patch_tag_not_found(logged_admin_client):
    url = reverse('tag-detail', kwargs={'slug': 'non-existing-slug'})
    payload = {'name': 'updated name'}
    response = logged_admin_client.patch(
        url, data=payload, content_type='application/json'
    )

    assert response.status_code == 404
    assert response.json()['error'] == 'Tag not found'


def test_patch_tag_invalid_fields(logged_admin_client, tag):
    payload = {
        'name': 'updated name',
        'invalid': 'invalid',
    }
    response = logged_admin_client.patch(
        path=reverse('tag-detail', kwargs={'slug': 'test-tag'}),
        data=payload,
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid fields: invalid'}


def test_patch_tag_json_decode_error(logged_admin_client, tag):
    payload = "'{invalid json"

    response = logged_admin_client.patch(
        path=reverse('tag-detail', kwargs={'slug': 'test-tag'}),
        data=payload,
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'Expecting value'


def test_patch_tag_validation_error(logged_admin_client, tag):
    payload = {
        'name': (
            'Lorem ipsum dolor sit amet, consectetuer '
            'adipiscing elit. Aenean commodo ligula eget dolor.'
        ),
    }

    response = logged_admin_client.patch(
        path=reverse('tag-detail', kwargs={'slug': 'test-tag'}),
        data=json.dumps(payload),
        content_type='application/json',
    )

    assert response.status_code == 400
    assert 'name' in response.json()['error'] and 'slug' in response.json()['error']


def test_patch_tag_generic_exception(logged_admin_client, override, tag):
    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    payload = {'name': 'test tag'}

    with override(Tag, 'save', fake_save):
        response = logged_admin_client.patch(
            path=reverse('tag-detail', kwargs={'slug': 'test-tag'}),
            data=json.dumps(payload),
            content_type='application/json',
        )

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
