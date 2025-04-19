from django.urls import reverse


def test_read_media_files(db, logged_admin_client, media_file_factory):
    media_file_factory.create_batch(3)
    url = reverse('media-list')
    response = logged_admin_client.get(url)

    assert response.status_code == 200
    assert len(response.json()['data']) == 3
