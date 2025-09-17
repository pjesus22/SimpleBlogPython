# import pytest
from django.urls import reverse

from apps.users.models import Author
from tests.unit_tests.api.conftest import build_expected_error


def test_get_users(db, logged_admin_client, admin_factory, author_factory):
    url = reverse('user-list')

    admin_factory.create()
    author_factory.create()

    response = logged_admin_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get('data')
    assert len(response_data.get('data')) == 3


def test_get_users_generic_error(
    db, logged_admin_client, author_factory, monkeypatch, fake_method_factory
):
    url = reverse('user-list')

    author_factory.create_batch(size=2)

    monkeypatch.setattr(
        'apps.users.views.users.User.objects.all',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_admin_client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong.',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data['errors']


def test_get_user_admin_auth(db, logged_admin_client, author_factory, post_factory):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})

    post_factory.create(author=user)

    response = logged_admin_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']
    assert response_data['data']['relationships']
    assert response_data['data']['included']


def test_get_user_author_auth(db, logged_author_client, post_factory):
    user = Author.objects.get(username='test_author')
    url = reverse('user-detail', kwargs={'pk': user.pk})

    post_factory.create(author=user)

    response = logged_author_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']
    assert response_data['data']['relationships']
    assert response_data['data']['included']


def test_get_user_not_found(db, logged_admin_client):
    url = reverse('user-detail', kwargs={'pk': 1000})

    response = logged_admin_client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='No User matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data['errors']


def test_get_user_does_not_have_permission(db, logged_author_client, author_factory):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})

    response = logged_author_client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='You do not have permission to view this user.',
        status=403,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data['errors']


def test_get_user_generic_error(
    db, logged_admin_client, author_factory, monkeypatch, fake_method_factory
):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})
    monkeypatch.setattr(
        'apps.users.views.users.get_object_or_404',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )
    response = logged_admin_client.get(url)
    response_data = response.json()
    expected = build_expected_error(
        detail='Something went wrong.',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )
    assert response.status_code == 500
    assert expected in response_data['errors']
