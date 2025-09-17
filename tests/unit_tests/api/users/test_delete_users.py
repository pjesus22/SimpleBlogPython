# import pytest
from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_delete_user_success(db, logged_admin_client, author_factory):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})

    response = logged_admin_client.delete(path=url)

    assert response.status_code == 204


def test_delete_user_not_found(db, logged_admin_client):
    url = reverse('user-detail', kwargs={'pk': 1000})

    response = logged_admin_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        detail='No User matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_delete_user_category_generic_exception(
    db, logged_admin_client, monkeypatch, fake_method_factory, author_factory
):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})

    monkeypatch.setattr(
        'apps.users.views.users.User.delete',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_admin_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong.',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data['errors']


def test_delete_user_does_not_have_permission(db, logged_author_client, author_factory):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})

    response = logged_author_client.delete(url, content_type='application/json')
    response_data = response.json()

    expected = build_expected_error(
        detail='You do not have permission to delete this user.',
        status=403,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data['errors']
