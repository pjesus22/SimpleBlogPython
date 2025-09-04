import pytest
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.users.models import Author
from tests.unit_tests.api.conftest import build_expected_error


def test_post_post_media_success(db, logged_author_client, post_factory):
    user = Author.objects.all().first()
    post = post_factory.create(author=user)
    test_file = File(open('tests/mock_data/alpaca.png', 'rb'))
    url = reverse('post-media-list', kwargs={'slug': post.slug})

    response = logged_author_client.post(
        path=url, data={'files': test_file}, format='multipart/form-data'
    )
    response_data = response.json()

    assert response.status_code == 201
    assert response_data['data']


def test_post_post_media_post_not_found(db, logged_author_client):
    url = reverse('post-media-list', kwargs={'slug': 'non-existing post slug'})

    response = logged_author_client.post(
        path=url, data={'files': 'invalid_file'}, format='multipart/form-data'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='No Post matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data['errors']


def test_post_post_media_unauthorized(db, logged_author_client, post_factory):
    post = post_factory.create()
    url = reverse('post-media-list', kwargs={'slug': post.slug})
    test_file = File(open('tests/mock_data/alpaca.png', 'rb'))

    response = logged_author_client.post(
        path=url, data={'files': test_file}, format='multipart/form-data'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='You do not have permission to add media files',
        status=403,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data['errors']


def test_post_post_media_generic_exception(
    db, logged_author_client, post_factory, monkeypatch, fake_method_factory
):
    user = Author.objects.all().first()
    post = post_factory.create(author=user)
    test_file = File(open('tests/mock_data/alpaca.png', 'rb'))
    url = reverse('post-media-list', kwargs={'slug': post.slug})

    monkeypatch.setattr(
        'apps.content.views.posts.media.MediaFile.save',
        fake_method_factory(raise_exception=Exception('Something went wrong')),
    )

    response = logged_author_client.post(
        path=url,
        data={'files': test_file},
        format='multipart',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data['errors']


@pytest.mark.parametrize(
    'payload, expected_error',
    [
        (
            {'files': SimpleUploadedFile(name='test_file.io', content=b'test_file')},
            'Invalid file type: .io is not allowed.',
        ),
        ({}, 'No files provided'),
    ],
)
def test_post_post_media_validation_errors(
    db, logged_author_client, post_factory, payload, expected_error
):
    user = Author.objects.all().first()
    post = post_factory.create(author=user)
    url = reverse('post-media-list', kwargs={'slug': post.slug})

    response = logged_author_client.post(
        path=url, data=payload, format='multipart/form-data'
    )
    response_data = response.json()

    expected = build_expected_error(
        detail=expected_error,
        status=400,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data['errors']
