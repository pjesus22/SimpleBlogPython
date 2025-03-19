import pytest
from django.urls import reverse

from apps.content.models import Tag

pytestmark = pytest.mark.django_db


def test_tag_list_view_returns_200(client, tag_factory):
    tag_factory.create_batch(size=3)

    url = reverse('tag-list')
    response = client.get(url)
    response_data = response.json()
    tags = Tag.objects.all()

    assert response.status_code == 200
    assert 'data' in response_data
    assert len(response_data['data']) == tags.count()


def test_tag_detail_view_returns_200(client, tag_factory, post_factory):
    tag = tag_factory.create()

    post_factory.create_batch(size=3, tags=[tag])

    url = reverse('tag-detail', kwargs={'slug': tag.slug})
    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert 'included' in response_data
    assert len(response_data['included']) > 0


def test_tag_detail_view_returns_404(client):
    url = reverse('tag-detail', kwargs={'slug': 'non-existing-slug'})
    response = client.get(url)
    expected_response = {'error': 'Tag non-existing-slug not found'}

    assert response.status_code == 404
    assert response.json() == expected_response
