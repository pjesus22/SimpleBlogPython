from django.urls import reverse

from apps.users.models import Author
from tests.unit_tests.api.conftest import build_expected_error


def test_patch_post_success(
    db, logged_author_client, post_factory, category_factory, tag_factory
):
    post = post_factory.create(author=Author.objects.all().first())
    new_category = category_factory.create(name='Updated Category')
    new_tag = tag_factory.create(name='Updated Tag')

    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {
        'content': 'Updated Content',
        'category': new_category.slug,
        'tags': [new_tag.slug],
    }

    response = logged_author_client.patch(
        path=url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']['attributes']['content'] == 'Updated Content'
    assert response_data['data']['relationships']['category']['data']['id'] == str(
        new_category.id
    )
    assert response_data['data']['relationships']['tags']['data'][0]['id'] == str(
        new_tag.id
    )


def test_patch_post_empty_field(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'content': ''}

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='This field cannot be blank.',
        status=400,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')


def test_patch_post_not_found(db, logged_admin_client):
    url = reverse('post-detail', kwargs={'slug': 'not-found'})
    payload = {'content': 'updated content'}

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='No Post matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_patch_do_not_have_permission(
    db, logged_author_client, post_factory, author_factory
):
    user = author_factory.create(username='testuser')
    post = post_factory.create(author=user)
    payload = {'content': 'updated content'}
    url = reverse('post-detail', kwargs={'slug': post.slug})

    response = logged_author_client.patch(
        path=url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='You do not have permission to edit this post',
        status=403,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data.get('errors')


def test_patch_post_invalid_fields(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'invalid': 'Invalid field'}

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


def test_patch_post_category_not_found(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'category': 'invalid-category'}

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='No Category matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_patch_post_tag_not_found(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'tags': ['invalid-tag']}

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='The following tags were not found: invalid-tag.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_patch_post_json_decode_error(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = "'{invalid json"

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Invalid JSON: Expecting value: line 1 column 1 (char 0)',
        status=400,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')


def test_patch_post_validation_error(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'title': 'X' * 51}

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )

    expected = build_expected_error(
        detail='Ensure this value has at most 50 characters (it has 51).',
        status=400,
        meta=response.json()['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response.json().get('errors')


def test_patch_post_generic_exception(
    db, logged_admin_client, post_factory, monkeypatch, fake_method_factory
):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'content': 'updated content'}

    monkeypatch.setattr(
        'apps.content.views.posts.detail.Post.save',
        fake_method_factory(raise_exception=Exception('Something went wrong')),
    )

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong',
        status=500,
        meta=response.json()['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')
