import json

from django.urls import reverse

from apps.content.models import Tag


def test_post_tag_success(db, logged_admin_client):
    payload = {'name': 'test tag'}

    response = logged_admin_client.post(
        path=reverse('tag-list'),
        data=json.dumps(payload),
        content_type='application/json',
    )

    response_data = response.json()

    assert response.status_code == 201
    assert 'data' in response_data
    assert response_data['data']['attributes']['name'] == 'test tag'


def test_post_category_invalid_fields(db, logged_admin_client):
    payload = {
        'name': 'test tag',
        'invalid': 'invalid',
    }

    response = logged_admin_client.post(
        path=reverse('tag-list'),
        data=json.dumps(payload),
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid fields: invalid'}


def test_post_tag_json_decode_error(db, logged_admin_client):
    payload = "'{invalid json"

    response = logged_admin_client.post(
        path=reverse('tag-list'),
        data=payload,
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'Expecting value'


def test_post_category_validation_error(db, logged_admin_client):
    payload = {
        'name': (
            'Lorem ipsum dolor sit amet, consectetuer '
            'adipiscing elit. Aenean commodo ligula eget dolor.'
        ),
    }

    response = logged_admin_client.post(
        path=reverse('tag-list'),
        data=json.dumps(payload),
        content_type='application/json',
    )

    assert response.status_code == 400
    assert 'name' in response.json()['error'] and 'slug' in response.json()['error']


def test_post_category_generic_exception(db, logged_admin_client, override):
    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    payload = {
        'name': 'test tag',
    }

    with override(Tag, 'save', fake_save):
        response = logged_admin_client.post(
            path=reverse('tag-list'),
            data=json.dumps(payload),
            content_type='application/json',
        )

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
