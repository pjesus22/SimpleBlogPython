import json

from django.urls import reverse

from apps.users.models import User


def test_user_success(db, logged_admin_client):
    payload = {
        'username': 'test-user',
        'email': 'test-user@example.com',
        'password': 'pollofrito',
        'role': 'author',
    }

    response = logged_admin_client.post(
        path=reverse('user-list'),
        data=json.dumps(payload),
        content_type='application/json',
    )

    response_data = response.json()

    assert response.status_code == 201
    assert 'data' in response_data
    assert response_data['data']['attributes']['username'] == 'test-user'
    assert response_data['data']['attributes']['email'] == 'test-user@example.com'


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

    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid fields: invalid'}


def test_post_user_json_decode_error(db, logged_admin_client):
    payload = "'{invalid json"

    response = logged_admin_client.post(
        path=reverse('user-list'),
        data=payload,
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'Expecting value'


def test_post_user_validation_error(db, logged_admin_client):
    payload = {
        'username': 'test-user',
        'email': (
            'Lorem ipsum dolor sit amet, consectetuer '
            'adipiscing elit. Aenean commodo ligula eget dolor.'
        ),
        'password': 'pollofrito',
        'role': (
            'Lorem ipsum dolor sit amet, consectetuer '
            'adipiscing elit. Aenean commodo ligula eget dolor.'
        ),
    }

    response = logged_admin_client.post(
        path=reverse('user-list'),
        data=json.dumps(payload),
        content_type='application/json',
    )

    assert response.status_code == 400
    assert 'email' in response.json()['error'] and 'role' in response.json()['error']


def test_post_user_generic_exception(db, logged_admin_client, override):
    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    payload = {
        'username': 'test-user',
        'email': 'test-user@example.com',
        'password': 'pollofrito',
        'role': 'author',
    }

    with override(User, 'save', fake_save):
        response = logged_admin_client.post(
            path=reverse('user-list'),
            data=json.dumps(payload),
            content_type='application/json',
        )

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
