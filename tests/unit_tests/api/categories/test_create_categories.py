import json

import pytest
from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_post_category_201_created(db, logged_admin_client):
    payload = {'name': 'test category', 'description': 'fake category description'}
    url = reverse('category-list')

    response = logged_admin_client.post(
        path=url, data=json.dumps(payload), content_type='application/json'
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    'payload, detailed_error',
    [
        (
            {
                'name': 'test category',
                'description': 'fake category description',
                'invalid': 'Invalid field',
            },
            'This field is not allowed.',
        ),
        ("'{invalid json", 'Invalid JSON: Expecting value: line 1 column 1 (char 0)'),
        (
            {'name': 'x' * 51},
            'Ensure this value has at most 50 characters (it has 51).',
        ),
        ({'name': ''}, 'This field cannot be blank.'),
    ],
)
def test_post_category_validation_errors(
    db, logged_admin_client, payload, detailed_error
):
    url = reverse('category-list')
    data = json.dumps(payload) if isinstance(payload, dict) else payload

    response = logged_admin_client.post(
        path=url, data=data, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detailed_error, meta=response_data['errors'][0]['meta']
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')


def test_post_category_generic_exception(
    db, monkeypatch, logged_admin_client, fake_method_factory
):
    payload = {'name': 'test category', 'description': 'fake category description'}
    url = reverse('category-list')

    monkeypatch.setattr(
        'apps.content.views.categories.Category.save',
        fake_method_factory(raise_exception=Exception('Something went wrong')),
    )

    response = logged_admin_client.post(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')
