import pytest
from django.urls import reverse

from apps.users.models import Author
from tests.unit_tests.api.conftest import build_expected_error


def test_get_posts_public_success(db, client, post_factory):
    post_factory.create_batch(size=2, status='published')
    url = reverse('post-list')

    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data['data']) == 2


def test_get_posts_private_success(db, logged_author_client, post_factory):
    url = reverse('post-list')
    user = Author.objects.all().first()
    post_factory.create_batch(size=2, author=user)

    response = logged_author_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data['data']) == 2


def test_get_posts_by_category(db, client, post_factory, category_factory):
    category = category_factory.create()
    another_category = category_factory.create()
    url = reverse('post-list')

    post_factory.create_batch(size=2, category=category, status='published')
    post_factory.create_batch(size=2, category=another_category, status='published')

    response = client.get(url, {'category': category.slug})
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data['data']) == 2


def test_get_posts_by_tags(db, client, post_factory, tag_factory):
    url = reverse('post-list')
    tags = tag_factory.create_batch(2)

    post_factory.create_batch(size=2, tags=tags, status='published')
    post_factory.create_batch(size=2, status='published')

    response = client.get(url, {'tags': f'{tags[0].name},{tags[1].name}'})
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data['data']) == 2


def test_get_posts_by_search(db, client, post_factory):
    url = reverse('post-list')

    post_factory.create(status='published')
    post_factory.create(title='Another Post', status='published')

    response = client.get(url, {'search': 'another'})
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data'][0]['attributes']['title'] == 'Another Post'
    assert len(response_data['data']) == 1


@pytest.mark.parametrize(
    'param_name, invalid_value, expected_error_msg',
    [
        ('category', 'invalid@category', 'Invalid slug format.'),
        ('tags', 'invalid@tag', 'Invalid slug format.'),
        ('search', 'invalid@search', 'Invalid search query format.'),
    ],
)
def test_get_posts_invalid_format(
    db, client, param_name, invalid_value, expected_error_msg
):
    url = reverse('post-list')
    params = {param_name: invalid_value}

    response = client.get(url, params)
    response_data = response.json()

    expected = build_expected_error(
        detail=expected_error_msg, status=400, meta=response_data['errors'][0]['meta']
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')


@pytest.mark.parametrize(
    'param_name, invalid_value, expected_error_msg',
    [
        ('category', 'non-existing', 'No Category matches the given query.'),
        (
            'tags',
            'non-existing-tag',
            'The following tags were not found: non-existing-tag.',
        ),
        ('search', 'non-existing-search', 'No Post matches the given query.'),
    ],
)
def test_get_posts_filter_by_relationship_not_found(
    db, client, post_factory, tag_factory, param_name, invalid_value, expected_error_msg
):
    url = reverse('post-list')
    params = {param_name: invalid_value}

    response = client.get(url, params)
    response_data = response.json()

    expected = build_expected_error(
        detail=expected_error_msg,
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_get_posts_generic_error(
    db, client, post_factory, monkeypatch, fake_method_factory
):
    post_factory.create()
    url = reverse('post-list')

    monkeypatch.setattr(
        'apps.content.views.posts.list.PostListView.get_queryset',
        fake_method_factory(raise_exception=Exception('Something went wrong')),
    )

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')


def test_get_post_public(db, client, post_factory):
    post = post_factory.create(status='published')
    url = reverse('post-detail', kwargs={'slug': post.slug})

    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']
    assert response_data['data']['included']


def test_get_post_private(db, logged_author_client, post_factory):
    post = post_factory.create(author=Author.objects.all().first())
    url = reverse('post-detail', kwargs={'slug': post.slug})

    response = logged_author_client.get(url)

    assert response.status_code == 200


def test_get_post_not_found(db, client, post_factory):
    url = reverse('post-detail', kwargs={'slug': 'not-found'})

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='No Post matches the given query.',
        status=404,
        title='Not Found',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_get_post_forbidden(db, client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='You do not have permission to view this post',
        status=403,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data.get('errors')


def test_get_post_generic_error(
    db, client, post_factory, monkeypatch, fake_method_factory
):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})

    monkeypatch.setattr(
        'apps.content.views.posts.detail.get_object_or_404',
        fake_method_factory(raise_exception=Exception('Something went wrong')),
    )

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')
