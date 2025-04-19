import json

from django.urls import reverse

from apps.content.models import Post


def test_post_post_success(db, logged_author_client, category_factory, tag_factory):
    category = category_factory.create()
    tags = tag_factory.create_batch(2)
    url = reverse('post-list')
    payload = {
        'title': 'Lorem ipsum',
        'content': 'Lorem ipsum dolor sit amet',
        'category': category.slug,
        'tags': [f'{tag.slug}' for tag in tags],
    }
    response = logged_author_client.post(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    response_data = response.json()
    assert response.status_code == 201
    assert 'data' in response_data
    assert response_data['data']['attributes']['title'] == payload['title']
    assert response_data['data']['attributes']['content'] == payload['content']
    assert response_data['data']['relationships']['category']['data']['id'] == str(
        category.pk
    )
    assert len(response_data['data']['relationships']['tags']['data']) == 2


def test_post_post_invalid_fields(db, logged_author_client, category_factory):
    category = category_factory.create()
    url = reverse('post-list')
    payload = {
        'title': 'Lorem ipsum',
        'content': 'Lorem ipsum dolor sit amet',
        'category': category.slug,
        'invalid_field': 'Lorem ipsum',
    }
    response = logged_author_client.post(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid fields: invalid_field'


def test_post_post_category_is_required(db, logged_author_client):
    url = reverse('post-list')
    payload = {
        'title': 'Lorem ipsum',
        'content': 'Lorem ipsum dolor sit amet',
    }
    response = logged_author_client.post(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    assert response.status_code == 400
    assert response.json()['error'] == 'Category is required'


def test_post_post_category_not_found(db, logged_author_client):
    url = reverse('post-list')
    payload = {
        'title': 'Lorem ipsum',
        'content': 'Lorem ipsum dolor sit amet',
        'category': 'not-found',
    }
    response = logged_author_client.post(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    assert response.status_code == 404
    assert response.json()['error'] == 'Category not found'


def test_post_post_tag_not_found(db, logged_author_client, category_factory):
    category = category_factory.create()
    url = reverse('post-list')
    payload = {
        'title': 'Lorem ipsum',
        'content': 'Lorem ipsum dolor sit amet',
        'category': category.slug,
        'tags': ['invalid-tag', 'another-invalid-tag'],
    }
    response = logged_author_client.post(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    assert response.status_code == 404
    assert all(
        [b in response.json()['error'] for b in ['invalid-tag', 'another-invalid-tag']]
    )


def test_post_post_json_decode_error(db, logged_author_client):
    url = reverse('post-list')
    payload = "'{invalid json"
    response = logged_author_client.post(
        path=url, data=payload, content_type='application/json'
    )
    assert response.status_code == 400
    assert response.json()['error'] == 'Expecting value'


def test_post_post_validation_error(db, logged_author_client, category_factory):
    category = category_factory.create()
    url = reverse('post-list')
    payload = {
        'title': (
            'Lorem ipsum dolor sit amet, consectetuer '
            'adipiscing elit. Aenean commodo ligula eget dolor.'
        ),
        'content': 'Lorem ipsum dolor sit amet',
        'category': category.slug,
    }
    response = logged_author_client.post(
        path=url, data=json.dumps(payload), content_type='application/json'
    )
    assert response.status_code == 400
    assert 'title' in response.json()['error']


def test_post_post_generic_exception(
    db, logged_author_client, override, category_factory
):
    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    category = category_factory.create()
    url = reverse('post-list')
    payload = {
        'title': 'Lorem ipsum',
        'content': 'Lorem ipsum dolor sit amet',
        'category': category.slug,
    }

    with override(Post, 'save', fake_save):
        response = logged_author_client.post(
            path=url, data=json.dumps(payload), content_type='application/json'
        )

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
