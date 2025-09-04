from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_get_media_files(db, logged_admin_client, media_file_factory):
    url = reverse('media-list')

    media_file_factory.create_batch(2)

    response = logged_admin_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data['data']) == 2


def test_get_media_files_generic_error(
    db, logged_admin_client, media_file_factory, monkeypatch, fake_method_factory
):
    url = reverse('media-list')

    media_file_factory.create_batch(2)

    monkeypatch.setattr(
        'apps.media_files.views.MediaFile.objects.all',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_admin_client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong.',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data['errors']


def test_get_media_file_success(db, logged_admin_client, media_file_factory):
    url = reverse('media-detail', kwargs={'id': 1})

    media_file_factory.create_batch(size=2)

    response = logged_admin_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']


def test_get_media_file_not_found(db, logged_admin_client, media_file_factory):
    url = reverse('media-detail', kwargs={'id': 1})

    response = logged_admin_client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='No MediaFile matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data['errors']


def test_get_media_file_generic_error(
    db, logged_admin_client, media_file_factory, monkeypatch, fake_method_factory
):
    url = reverse('media-detail', kwargs={'id': 1})

    media_file_factory.create()

    monkeypatch.setattr(
        'apps.media_files.views.get_object_or_404',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_admin_client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong.',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data['errors']
