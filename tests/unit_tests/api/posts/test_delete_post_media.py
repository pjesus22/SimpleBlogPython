from django.urls import reverse

from apps.users.models import Admin
from tests.unit_tests.api.conftest import build_expected_error


def test_delete_post_media_success(
    db, logged_admin_client, post_factory, media_file_factory
):
    user = Admin.objects.all().first()
    post = post_factory.create(author=user)
    media_file = media_file_factory.create(post=post)
    url = reverse('post-media-detail', kwargs={'slug': post.slug, 'id': media_file.id})

    response = logged_admin_client.delete(url)

    assert response.status_code == 204


def test_delete_post_media_unauthorized(
    db, logged_author_client, post_factory, media_file_factory, author_factory
):
    user = author_factory.create(username='testuser')
    post = post_factory.create(author=user)
    media_file = media_file_factory.create(post=post)

    url = reverse('post-media-detail', kwargs={'slug': post.slug, 'id': media_file.id})

    response = logged_author_client.delete(url)
    response_data = response.json()

    expected = build_expected_error(
        status=403,
        detail='You do not have permission to delete this media file',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data.get('errors')


def test_delete_post_media_post_not_found(db, logged_admin_client):
    url = reverse('post-media-detail', kwargs={'slug': 'non-existing-slug', 'id': '0'})

    response = logged_admin_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        status=404,
        detail='No MediaFile matches the given query.',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_delete_post_media_generic_exception(
    db,
    logged_admin_client,
    post_factory,
    media_file_factory,
    monkeypatch,
    fake_method_factory,
):
    post = post_factory.create()
    media_file = media_file_factory.create(post=post)
    url = reverse('post-media-detail', kwargs={'slug': post.slug, 'id': media_file.id})

    monkeypatch.setattr(
        'apps.content.views.posts.media.MediaFile.delete',
        fake_method_factory(raise_exception=Exception('Something went wrong')),
    )

    response = logged_admin_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        status=500,
        detail='Something went wrong',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')
