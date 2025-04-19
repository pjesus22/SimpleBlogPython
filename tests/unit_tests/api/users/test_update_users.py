import json

import pytest
from django.urls import reverse

from apps.users.models import User


@pytest.fixture
def author_user(db, author_factory):
    return author_factory.create(username='author', email='author@example.com')


def test_patch_user_success(db, logged_admin_client, author_user):
    url = reverse('user-detail', kwargs={'pk': author_user.pk})
    payload = {'email': 'updated@email.com'}
    response = logged_admin_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['data']['attributes']['email'] == 'updated@email.com'


def test_patch_user_not_found(db, logged_admin_client):
    url = reverse('user-detail', kwargs={'pk': 1000})
    payload = {'email': 'updated@email.com'}
    response = logged_admin_client.patch(
        url, data=payload, content_type='application/json'
    )

    assert response.status_code == 404
    assert response.json()['error'] == 'User not found'


def test_patch_user_does_not_have_permission(db, logged_author_client, author_user):
    url = reverse('user-detail', kwargs={'pk': author_user.pk})
    payload = {'email': 'updated@email.com'}
    response = logged_author_client.patch(
        url, data=payload, content_type='application/json'
    )

    assert response.status_code == 403
    assert response.json()['error'] == 'Permission denied'


def test_patch_user_invalid_fields(db, logged_admin_client, author_user):
    url = reverse('user-detail', kwargs={'pk': author_user.pk})
    payload = {
        'email': 'updated@email.com',
        'invalid': 'invalid',
    }
    response = logged_admin_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid fields: invalid'}


def test_patch_user_json_decode_error(db, logged_admin_client, author_user):
    url = reverse('user-detail', kwargs={'pk': author_user.pk})
    payload = "'{invalid json"

    response = logged_admin_client.patch(
        path=url,
        data=payload,
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'Expecting value'


def test_patch_user_validation_error(db, logged_admin_client, author_user):
    url = reverse('user-detail', kwargs={'pk': author_user.pk})
    payload = {
        'username': (
            'Lorem ipsum dolor sit amet, consectetuer '
            'adipiscing elit. Aenean commodo ligula eget dolor.'
        ),
    }

    response = logged_admin_client.patch(
        path=url,
        data=json.dumps(payload),
        content_type='application/json',
    )

    assert response.status_code == 400
    assert 'username' in response.json()['error']


def test_patch_user_generic_exception(db, logged_admin_client, override, author_user):
    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    payload = {'email': 'updated@email.com'}

    with override(User, 'save', fake_save):
        response = logged_admin_client.patch(
            path=reverse('user-detail', kwargs={'pk': author_user.pk}),
            data=json.dumps(payload),
            content_type='application/json',
        )

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
