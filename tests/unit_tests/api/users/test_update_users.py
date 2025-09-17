import json

# import pytest
from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_patch_user_success(db, logged_admin_client, author_factory):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})
    payload = {'email': 'updated@email.com', 'password': 'newpassword123'}

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']['attributes']['email'] == 'updated@email.com'


def test_patch_user_not_found(db, logged_admin_client):
    url = reverse('user-detail', kwargs={'pk': 1000})
    payload = {'email': 'updated@email.com'}

    response = logged_admin_client.patch(
        url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='No User matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_patch_user_does_not_have_permission(db, logged_author_client, author_factory):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})
    payload = {'email': 'updated@email.com'}

    response = logged_author_client.patch(
        url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='You do not have permission to edit this user.',
        status=403,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data.get('errors')


def test_patch_user_invalid_fields(db, logged_admin_client, author_factory):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})
    payload = {'invalid': 'invalid'}

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='This field is not allowed.',
        status=400,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')


def test_patch_user_json_decode_error(db, logged_admin_client, author_factory):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})
    payload = "'{invalid json"

    response = logged_admin_client.patch(path=url, data=payload)
    response_data = response.json()

    expected = build_expected_error(
        detail='Expecting value: line 1 column 1 (char 0)',
        status=400,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    expected in response_data.get('errors')


def test_patch_user_validation_error(db, logged_admin_client, author_factory):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})
    payload = {'username': 'x' * 151}

    response = logged_admin_client.patch(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Ensure this value has at most 150 characters (it has 151).',
        status=400,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')


def test_patch_user_generic_exception(
    db, logged_admin_client, author_factory, monkeypatch, fake_method_factory
):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})
    payload = {'email': 'updated@email.com'}

    monkeypatch.setattr(
        'apps.users.views.users.User.save',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_admin_client.patch(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong.',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')


def test_patch_user_invalid_password(db, logged_admin_client, author_factory):
    user = author_factory.create()
    url = reverse('user-detail', kwargs={'pk': user.pk})
    payload = {'password': 'short'}

    response = logged_admin_client.patch(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='This password is too short. It must contain at least 8 characters.',
        status=400,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')
