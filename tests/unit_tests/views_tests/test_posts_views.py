import pytest
from django.urls import reverse

from apps.content.models import Post

pytestmark = pytest.mark.django_db


def test_post_list_view_returns_200(client, post_factory, admin_factory):
    user = admin_factory.create(username='test-user')

    client.force_login(user)
    post_factory.create_batch(size=3, author=user)

    url = reverse('post-list')
    response = client.get(url)
    response_data = response.json()
    posts = Post.objects.all()

    assert response.status_code == 200
    assert 'data' in response_data
    assert len(response_data['data']) == posts.count()


def test_post_detail_view_returns_200(client, post_factory, admin_factory):
    user = admin_factory.create(username='test-user')

    client.force_login(user)

    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert 'included' in response_data
    assert len(response_data['included']) > 0


def test_post_detail_view_returns_404(client):
    url = reverse('post-detail', kwargs={'slug': 'non-existing-slug'})
    response = client.get(url)
    expected_response = {'error': 'Post non-existing-slug not found'}

    assert response.status_code == 404
    assert response.json() == expected_response
