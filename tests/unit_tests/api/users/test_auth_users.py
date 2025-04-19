import json

import pytest
from django.urls import reverse


@pytest.fixture
def test_user(db, author_factory):
    user = author_factory.create(username='testuser')
    return user


def test_csrf_token_view(csrf_client):
    url = reverse('csrf-token')
    response = csrf_client.get(url)

    assert response.status_code == 200
    assert 'token' in response.json()


def test_login_success(db, csrf_client, test_user):
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = {
        'username': 'testuser',
        'password': 'password',
    }

    response = csrf_client.post(
        url,
        data=payload,
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 200
    assert response.json()['message'] == 'Successfully logged in'
    assert response.json()['user'] == 'testuser'


def test_login_missing_fields(csrf_client):
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = {
        'username': 'testuser',
    }

    response = csrf_client.post(
        url,
        data=payload,
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 400
    assert response.json() == {'error': 'Both username and password are required'}


def test_login_invalid_credentials(csrf_client, test_user):
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = {
        'username': 'testuser',
        'password': 'wrongpassword',
    }

    response = csrf_client.post(
        url,
        data=payload,
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 401
    assert response.json() == {'error': 'Invalid credentials'}


def test_login_invalid_fields(csrf_client):
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = {
        'username': 'testuser',
        'password': 'password',
        'invalid': 'invalid',
    }

    response = csrf_client.post(
        url,
        data=payload,
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid fields: invalid'}


def test_login_json_decode_error(csrf_client):
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = "'{invalid json"

    response = csrf_client.post(
        url,
        data=payload,
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid JSON format'}


def test_login_generic_exception(csrf_client, test_user, override):
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = {
        'username': 'testuser',
        'password': 'password',
    }

    def raise_exception(*args, **kwargs):
        raise Exception('Something went wrong')

    with override(json, 'loads', raise_exception):
        response = csrf_client.post(
            url,
            data=payload,
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )

    assert response.status_code == 500
    assert response.json() == {'error': 'Something went wrong'}


def test_logout_success(db, logged_author_client):
    url = reverse('logout')

    response = logged_author_client.post(
        url,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['message'] == 'Successfully logged out'


def test_logout_without_authentication(client):
    response = client.post(reverse('logout'))

    assert response.status_code == 401
    assert response.json() == {'error': 'No authenticated user'}
