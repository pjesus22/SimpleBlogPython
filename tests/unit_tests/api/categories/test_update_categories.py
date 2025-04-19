import json

import pytest
from django.urls import reverse

from apps.content.models import Category


@pytest.fixture
def category(category_factory):
    return category_factory.create(
        name='test category', description='fake category description'
    )


def test_patch_category_success(db, logged_admin_client, category):
    url = reverse('category-detail', kwargs={'slug': 'test-category'})
    payload = {'description': 'updated description'}
    response = logged_admin_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['data']['attributes']['description'] == 'updated description'


def test_patch_category_not_found(db, logged_admin_client):
    url = reverse('category-detail', kwargs={'slug': 'non-existing-slug'})
    payload = {'name': 'updated name', 'description': 'updated description'}
    response = logged_admin_client.patch(
        url, data=payload, content_type='application/json'
    )

    assert response.status_code == 404
    assert response.json()['error'] == 'Category not found'


def test_patch_category_invalid_fields(db, logged_admin_client, category):
    payload = {
        'name': 'updated name',
        'description': 'updated description',
        'invalid': 'invalid',
    }
    response = logged_admin_client.patch(
        path=reverse('category-detail', kwargs={'slug': 'test-category'}),
        data=payload,
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid fields: invalid'}


def test_patch_category_json_decode_error(db, logged_admin_client, category):
    payload = "'{invalid json"

    response = logged_admin_client.patch(
        path=reverse('category-detail', kwargs={'slug': 'test-category'}),
        data=payload,
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'Expecting value'


def test_patch_category_validation_error(db, logged_admin_client, category):
    payload = {
        'name': (
            'Lorem ipsum dolor sit amet, consectetuer '
            'adipiscing elit. Aenean commodo ligula eget dolor.'
        ),
        'description': 'fake category description',
    }

    response = logged_admin_client.patch(
        path=reverse('category-detail', kwargs={'slug': 'test-category'}),
        data=json.dumps(payload),
        content_type='application/json',
    )

    assert response.status_code == 400
    assert 'name' in response.json()['error'] and 'slug' in response.json()['error']


def test_patch_category_generic_exception(db, logged_admin_client, override, category):
    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    payload = {
        'name': 'test category',
        'description': 'fake category description',
    }

    with override(Category, 'save', fake_save):
        response = logged_admin_client.patch(
            path=reverse('category-detail', kwargs={'slug': 'test-category'}),
            data=json.dumps(payload),
            content_type='application/json',
        )

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
