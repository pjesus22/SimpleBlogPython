import json

import pytest
from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_post_post_success(db, logged_author_client, category_factory, tag_factory):
    category_factory.create(name='Test Category')
    url = reverse('post-list')
    payload = {
        'title': 'Test Post Title',
        'content': 'This is the content of the test post.',
        'category': 'test-category',
    }

    response = logged_author_client.post(
        path=url, data=json.dumps(payload), content_type='application/json'
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    'payload, detailed_error',
    [
        (
            {
                'title': 'Test Post Title',
                'content': 'This is the content of the test post.',
                'category': 'test-category',
                'invalid': 'invalid value',
            },
            'This field is not allowed.',
        ),
        (
            {
                'title': 'Test Post Title',
                'content': 'This is the content of the test post.',
            },
            'This field is required.',
        ),
        ("'{invalid json", 'Invalid JSON: Expecting value: line 1 column 1 (char 0)'),
        (
            {
                'title': ('X' * 51),
                'content': 'This is the content of the test post.',
                'category': 'test-category',
            },
            'Ensure this value has at most 50 characters (it has 51).',
        ),
    ],
)
def test_post_post_validation_errors(
    payload, detailed_error, db, logged_author_client, category_factory
):
    category_factory.create(name='Test Category')
    url = reverse('post-list')
    data = json.dumps(payload) if isinstance(payload, dict) else payload

    response = logged_author_client.post(
        path=url, data=data, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detailed_error, meta=response_data['errors'][0]['meta']
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')


@pytest.mark.parametrize(
    'payload, detailed_error',
    [
        ({'category': 'not-found'}, 'No Category matches the given query.'),
        (
            {'category': 'test-category', 'tags': ['invalid-tag']},
            'The following tags were not found: invalid-tag.',
        ),
    ],
)
def test_post_post_attribute_not_found(
    payload, detailed_error, db, logged_author_client, category_factory, tag_factory
):
    category_factory.create(name='Test Category')
    url = reverse('post-list')
    payload.update(
        {
            'title': 'Test Post Title',
            'content': 'This is the content of the test post.',
        }
    )
    response = logged_author_client.post(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail=detailed_error,
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_post_post_generic_exception(
    db, logged_author_client, category_factory, monkeypatch, fake_method_factory
):
    category = category_factory.create()
    url = reverse('post-list')
    payload = {
        'title': 'Test Post Title',
        'content': 'This is the content of the test post.',
        'category': category.slug,
    }

    monkeypatch.setattr(
        'apps.content.views.posts.list.Post.save',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_author_client.post(
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
