from django.urls import reverse

from apps.users.models import Author
from tests.unit_tests.api.conftest import build_expected_error


def test_get_post_media_public(db, client, post_factory, media_file_factory):
    post = post_factory.create(status='published')
    url = reverse('post-media-list', kwargs={'slug': post.slug})

    media_file_factory.create_batch(size=2, post=post)

    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data['data']) == 2


def test_get_post_media_private_success(
    db, logged_author_client, post_factory, media_file_factory
):
    post = post_factory.create(author=Author.objects.all().first())
    url = reverse('post-media-list', kwargs={'slug': post.slug})

    media_file_factory.create_batch(size=2, post=post)

    response = logged_author_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data['data']) == 2


def test_get_post_media_private_not_authorized(
    db, client, post_factory, media_file_factory
):
    post = post_factory.create()
    url = reverse('post-media-list', kwargs={'slug': post.slug})

    media_file_factory.create_batch(size=2, post=post)

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='You do not have permission to view these media files',
        status=403,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data.get('errors')


def test_get_post_media_post_not_found(db, client):
    url = reverse('post-media-list', kwargs={'slug': 'not-found'})

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        status=404,
        detail='No Post matches the given query.',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_get_post_media_generic_error(
    db,
    logged_author_client,
    post_factory,
    media_file_factory,
    monkeypatch,
    fake_method_factory,
):
    post = post_factory.create(author=Author.objects.all().first())
    url = reverse('post-media-list', kwargs={'slug': post.slug})

    media_file_factory.create_batch(size=2, post=post)

    monkeypatch.setattr(
        'apps.content.views.posts.media.Post.objects.all',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_author_client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        status=500,
        detail='Something went wrong.',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')


def test_get_post_media_item_public(db, client, post_factory, media_file_factory):
    post = post_factory.create(status='published')
    media_file = media_file_factory.create(post=post)
    url = reverse(
        'post-media-detail', kwargs={'slug': post.slug, 'id': str(media_file.id)}
    )

    response = client.get(url)

    assert response.status_code == 200


def test_get_post_media_item_private(
    db, logged_author_client, post_factory, media_file_factory
):
    post = post_factory.create(author=Author.objects.all().first())
    media_file = media_file_factory.create(post=post)
    url = reverse(
        'post-media-detail', kwargs={'slug': post.slug, 'id': str(media_file.id)}
    )

    response = logged_author_client.get(url)

    assert response.status_code == 200


def test_get_post_media_item_private_not_authorized(
    db, client, post_factory, media_file_factory
):
    post = post_factory.create()
    media_file = media_file_factory.create(post=post)
    url = reverse(
        'post-media-detail', kwargs={'slug': post.slug, 'id': str(media_file.id)}
    )

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        status=403,
        detail='You do not have permission to view this media file',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data.get('errors')


def test_get_post_media_item_not_found(db, client, post_factory):
    post = post_factory.create()
    url = reverse('post-media-detail', kwargs={'slug': post.slug, 'id': '0'})

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        status=404,
        detail='No MediaFile matches the given query.',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_get_post_media_item_generic_error(
    db,
    logged_author_client,
    post_factory,
    media_file_factory,
    monkeypatch,
    fake_method_factory,
):
    post = post_factory.create(author=Author.objects.all().first())
    media_file = media_file_factory.create(post=post)
    url = reverse(
        'post-media-detail', kwargs={'slug': post.slug, 'id': str(media_file.id)}
    )

    monkeypatch.setattr(
        'apps.content.views.posts.media.get_object_or_404',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_author_client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        status=500,
        detail='Something went wrong.',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')
