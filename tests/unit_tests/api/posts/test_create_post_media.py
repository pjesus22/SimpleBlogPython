from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.media_files.models import MediaFile
from apps.users.models import Author


def test_post_post_media_success(db, logged_author_client, post_factory):
    user = Author.objects.all().first()
    post = post_factory.create(author=user)
    test_file = File(open('tests/mock_data/alpaca.png', 'rb'))

    url = reverse('post-media-list', kwargs={'slug': post.slug})

    response = logged_author_client.post(
        path=url,
        data={'files': test_file},
        format='multipart',
    )

    print(response.json())
    assert response.status_code == 201
    assert 'data' in response.json()
    assert len(response.json()['data']) == 1


def test_post_post_media_post_not_found(db, logged_author_client):
    url = reverse('post-media-list', kwargs={'slug': 'non-existing post slug'})

    response = logged_author_client.post(
        path=url,
        data={'files': 'invalid_file'},
        format='multipart',
    )

    print(response.json())

    assert response.status_code == 404
    assert response.json()['error'] == 'Post not found'


def test_post_post_media_unauthorized(db, logged_author_client, post_factory):
    post = post_factory.create()
    url = reverse('post-media-list', kwargs={'slug': post.slug})
    test_file = File(open('tests/mock_data/alpaca.png', 'rb'))

    response = logged_author_client.post(
        path=url,
        data={'files': test_file},
        format='multipart',
    )

    assert response.status_code == 403
    assert response.json()['error'] == 'Permission denied'


def test_post_post_media_validation_error(db, logged_author_client, post_factory):
    user = Author.objects.all().first()
    post = post_factory.create(author=user)
    test_file = SimpleUploadedFile(name='test_file.io', content=b'test_file')
    url = reverse('post-media-list', kwargs={'slug': post.slug})

    response = logged_author_client.post(
        path=url,
        data={'files': test_file},
        format='multipart',
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid file type: .io is not allowed.'


def test_post_post_media_generic_exception(
    db, logged_author_client, post_factory, override
):
    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    user = Author.objects.all().first()
    post = post_factory.create(author=user)
    test_file = File(open('tests/mock_data/alpaca.png', 'rb'))
    url = reverse('post-media-list', kwargs={'slug': post.slug})

    with override(MediaFile, 'save', fake_save):
        response = logged_author_client.post(
            path=url,
            data={'files': test_file},
            format='multipart',
        )

    assert response.status_code == 500
    assert response.json()['error'] == 'Something went wrong'
