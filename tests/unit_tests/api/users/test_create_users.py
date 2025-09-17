import json

import pytest
from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_post_user_success(db, logged_admin_client):
    payload = {
        'username': 'test_user',
        'email': 'testuser@example.com',
        'password': 'pollofrito',
    }

    response = logged_admin_client.post(
        path=reverse('user-list'),
        data=json.dumps(payload),
        content_type='application/json',
    )

    response_data = response.json()

    assert response.status_code == 201
    assert response_data['data']
    assert response_data['data']['attributes']['username'] == 'test_user'
    assert response_data['data']['attributes']['email'] == 'testuser@example.com'


def test_post_user_invalid_fields(db, logged_admin_client):
    payload = {
        'username': 'test-user',
        'email': 'test-user@example.com',
        'password': 'pollofrito',
        'role': 'author',
        'invalid': 'invalid',
    }

    response = logged_admin_client.post(
        path=reverse('user-list'),
        data=json.dumps(payload),
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='This field is not allowed.', meta=response_data['errors'][0]['meta']
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')


def test_post_user_json_decode_error(db, logged_admin_client):
    payload = "'{invalid json"

    response = logged_admin_client.post(
        path=reverse('user-list'),
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Expecting value: line 1 column 1 (char 0)',
        meta=response_data['errors'][0]['meta'],
    )

    print(response_data)

    assert response.status_code == 400
    assert expected in response_data.get('errors')


@pytest.mark.parametrize(
    'payload, validation_error',
    [
        (
            {'username': 'invalid&name@/'},
            'Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.',
        ),
        ({'email': 'fake-email/format.com'}, 'Enter a valid email address.'),
        ({'password': 'password'}, 'This password is too common.'),
    ],
)
def test_post_user_validate_attributes(
    db, logged_admin_client, payload, validation_error
):
    base_payload = {
        'username': 'common_user',
        'email': 'common@example.com',
        'password': 'fake_password789',
    }
    base_payload.update(payload)

    response = logged_admin_client.post(
        path=reverse('user-list'),
        data=json.dumps(base_payload),
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail=validation_error, meta=response_data['errors'][0]['meta']
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')


def test_post_user_generic_exception(
    db, logged_admin_client, monkeypatch, fake_method_factory
):
    payload = {
        'username': 'test-user',
        'email': 'test-user@example.com',
        'password': 'pollofrito',
    }

    monkeypatch.setattr(
        'apps.users.views.users.User.save',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_admin_client.post(
        path=reverse('user-list'),
        data=json.dumps(payload),
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong.',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data['errors']
