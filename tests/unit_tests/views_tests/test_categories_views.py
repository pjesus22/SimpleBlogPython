import pytest
from django.urls import reverse

from apps.content.models import Category

pytestmark = pytest.mark.django_db


def test_category_list_view_returns_200(client, category_factory):
    category_factory.create_batch(size=3)

    url = reverse('category-list')
    response = client.get(url)
    response_data = response.json()
    categories = Category.objects.all()

    assert response.status_code == 200
    assert 'data' in response_data
    assert len(response_data['data']) == categories.count()


def test_category_detail_view_returns_200(client, category_factory, post_factory):
    category = category_factory.create()

    post_factory.create_batch(size=3, category=category)

    url = reverse('category-detail', kwargs={'slug': category.slug})
    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert 'included' in response_data
    assert len(response_data['included']) > 0


def test_category_detail_view_returns_404(client):
    url = reverse('category-detail', kwargs={'slug': 'non-existing-slug'})
    response = client.get(url)
    expected_response = {'error': 'Category non-existing-slug not found'}

    assert response.status_code == 404
    assert response.json() == expected_response
