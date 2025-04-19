import json

import pytest
from django.urls import reverse

from apps.content.models import Category


@pytest.fixture
def category(db, category_factory):
    return category_factory.create(
        name='test category', description='fake category description'
    )


def test_delete_category_success(db, logged_admin_client, category):
    url = reverse('category-detail', kwargs={'slug': category.slug})
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 204


def test_delete_category_not_found(db, logged_admin_client):
    url = reverse('category-detail', kwargs={'slug': 'non-existing-slug'})
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 404


def test_delete_category_generic_exception(db, logged_admin_client, override, category):
    def fake_delete(*args, **kwargs):
        raise Exception('Something went wrong')

    with override(Category, 'delete', fake_delete):
        response = logged_admin_client.delete(
            path=reverse('category-detail', kwargs={'slug': category.slug}),
            data=json.dumps(
                {
                    'name': 'test category',
                    'description': 'fake category description',
                }
            ),
        )

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
