import pytest
from django.urls import reverse

from apps.users.models import Author


@pytest.fixture
def admin_user(db, admin_factory):
    return admin_factory.create(username='admin', email='admin@example.com')


@pytest.fixture
def author_user(db, author_factory):
    return author_factory.create(username='author', email='author@example.com')


def test_get_users(db, logged_admin_client, admin_factory, author_factory):
    admin_factory.create_batch(size=2)
    author_factory.create_batch(size=2)

    url = reverse('user-list')
    response = logged_admin_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert len(response_data['data']) == 5


def test_get_user_admin_auth(db, logged_admin_client, post_factory, admin_user):
    post_factory.create_batch(size=3, author=admin_user)

    url = reverse('user-detail', kwargs={'pk': admin_user.pk})
    response = logged_admin_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert 'included' in response_data


def test_get_user_author_auth(db, logged_author_client, post_factory):
    user = Author.objects.get(username='test-author')
    post_factory.create_batch(size=3, author=user)

    url = reverse('user-detail', kwargs={'pk': user.pk})
    response = logged_author_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert 'included' in response_data


def test_get_user_not_found(db, logged_admin_client):
    url = reverse('user-detail', kwargs={'pk': 1000})
    response = logged_admin_client.get(url)
    expected_response = {'error': 'User not found'}

    assert response.status_code == 404
    assert response.json() == expected_response


def test_get_user_does_not_have_permission(db, logged_author_client, author_user):
    url = reverse('user-detail', kwargs={'pk': author_user.pk})
    response = logged_author_client.get(url)
    expected_response = {'error': 'Permission denied'}

    assert response.status_code == 403
    assert response.json() == expected_response
