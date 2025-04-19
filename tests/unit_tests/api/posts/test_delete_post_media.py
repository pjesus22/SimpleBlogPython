from django.urls import reverse

from apps.media_files.models import MediaFile
from apps.users.models import Admin


def test_delete_post_media_success(
    db, logged_admin_client, post_factory, media_file_factory
):
    user = Admin.objects.all().first()
    post = post_factory.create(author=user)
    media_file = media_file_factory.create(post=post)

    url = reverse('post-media-detail', kwargs={'slug': post.slug, 'id': media_file.id})

    response = logged_admin_client.delete(url)

    assert response.status_code == 204


def test_delete_post_media_post_not_found(db, logged_admin_client):
    url = reverse(
        'post-media-detail', kwargs={'slug': 'non-existing-slug', 'id': '1000'}
    )
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 404


def test_delete_post_media_unauthorized(
    db, logged_author_client, post_factory, media_file_factory, author_factory
):
    user = author_factory.create(username='testuser')
    post = post_factory.create(author=user)
    media_file = media_file_factory.create(post=post)

    url = reverse('post-media-detail', kwargs={'slug': post.slug, 'id': media_file.id})

    response = logged_author_client.delete(url)

    assert response.status_code == 403


def test_delete_post_media_generic_exception(
    db, logged_admin_client, post_factory, media_file_factory, override
):
    def fake_delete(*args, **kwargs):
        raise Exception('Something went wrong')

    post = post_factory.create()
    media_file = media_file_factory.create(post=post)

    url = reverse('post-media-detail', kwargs={'slug': post.slug, 'id': media_file.id})

    with override(MediaFile, 'delete', fake_delete):
        response = logged_admin_client.delete(path=url)

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
