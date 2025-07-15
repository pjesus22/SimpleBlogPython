from django.urls import reverse

from apps.content.models import Category
from tests.unit_tests.api.conftest import build_expected_error


def test_delete_category_success(db, logged_admin_client, category_factory):
    category_factory.create(name='Test Category')
    url = reverse('category-detail', kwargs={'slug': 'test-category'})

    response = logged_admin_client.delete(path=url)

    assert response.status_code == 204
    assert not Category.objects.filter(slug='test-category').exists()


def test_delete_category_not_found(db, logged_admin_client):
    url = reverse('category-detail', kwargs={'slug': 'non-existing-slug'})

    response = logged_admin_client.delete(path=url)

    assert response.status_code == 404


def test_delete_category_generic_exception(
    db,
    monkeypatch,
    logged_admin_client,
    category_factory,
    fake_method_factory,
):
    category_factory.create(name='Test Category')

    url = reverse('category-detail', kwargs={'slug': 'test-category'})

    monkeypatch.setattr(
        'apps.content.views.categories.Category.delete',
        fake_method_factory(raise_exception=Exception('Something went wrong')),
    )

    response = logged_admin_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')
