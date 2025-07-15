import json

import pytest
from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_patch_tag_success(db, logged_admin_client, tag_factory):
    tag_factory.create(name='Test Tag')

    payload = {'name': 'updated name'}
    url = reverse('tag-detail', kwargs={'slug': 'test-tag'})

    response = logged_admin_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']['attributes']['name'] == 'updated name'


def test_patch_tag_not_found(db, logged_admin_client):
    url = reverse('tag-detail', kwargs={'slug': 'non-existing-slug'})
    payload = {'name': 'updated name'}

    response = logged_admin_client.patch(
        url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='No Tag matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data['errors']


@pytest.mark.parametrize(
    'payload, expected',
    [
        (
            {'invalid': 'invalid'},
            build_expected_error(detail='This field is not allowed.'),
        ),
        (
            "'{invalid json",
            build_expected_error(
                detail='Invalid JSON: Expecting value: line 1 column 1 (char 0)'
            ),
        ),
        (
            {'name': 'x' * 51},
            build_expected_error(
                detail='Ensure this value has at most 50 characters (it has 51).'
            ),
        ),
        (
            {'name': ''},
            build_expected_error(detail='This field cannot be empty or null.'),
        ),
    ],
)
def test_patch_category_validation_errors(
    db, logged_admin_client, tag_factory, payload, expected
):
    tag_factory.create(name='Test Tag')

    url = reverse('tag-detail', kwargs={'slug': 'test-tag'})
    data = json.dumps(payload) if isinstance(payload, dict) else payload

    response = logged_admin_client.patch(
        path=url, data=data, content_type='application/json'
    )
    response_data = response.json()

    expected.update({'meta': response_data['errors'][0]['meta']})

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_patch_tag_generic_exception(
    db, logged_admin_client, tag_factory, monkeypatch, fake_method_factory
):
    tag_factory.create(name='Test Tag')
    payload = {'name': 'test tag'}

    monkeypatch.setattr(
        'apps.content.views.tags.Tag.save',
        fake_method_factory(raise_exception=Exception('Something went wrong')),
    )

    response = logged_admin_client.patch(
        path=reverse('tag-detail', kwargs={'slug': 'test-tag'}),
        data=json.dumps(payload),
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')
