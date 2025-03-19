import pytest
from django.urls import reverse

from apps.users.models import User

pytestmark = pytest.mark.django_db


def test_user_list_view_returns_200(client, admin_factory, author_factory):
    user = admin_factory.create(username='test-user')
    client.force_login(user)
    author_factory.create_batch(size=3)

    url = reverse('user-list')
    response = client.get(url)
    response_data = response.json()
    users = User.objects.all()

    assert response.status_code == 200
    assert 'data' in response_data
    assert len(response_data['data']) == users.count()


def test_user_detail_view_returns_200(client, author_factory):
    user = author_factory.create()
    client.force_login(user)

    url = reverse('user-detail', kwargs={'pk': user.pk})
    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert 'included' in response_data
    assert len(response_data['included']) > 0


def test_user_detail_view_returns_404(client, author_factory):
    user = author_factory.create()
    client.force_login(user)
    url = reverse('user-detail', kwargs={'pk': 100})
    response = client.get(url)
    expected_response = {'error': 'User with pk 100 not found'}

    assert response.status_code == 404
    assert response.json() == expected_response
