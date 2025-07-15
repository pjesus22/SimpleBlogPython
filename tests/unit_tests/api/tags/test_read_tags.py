from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_get_tag_list(db, client, tag_factory):
    tag_factory.create_batch(size=2)

    url = reverse('tag-list')

    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']
    assert len(response_data['data']) == 2


def test_get_tag_list_server_error(db, monkeypatch, client, fake_method_factory):
    url = reverse('tag-list')

    monkeypatch.setattr(
        'apps.content.views.tags.Tag.objects.all',
        fake_method_factory(raise_exception=Exception('Database connection failed')),
    )

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Database connection failed',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')


def test_get_single_tag(db, client, tag_factory, post_factory):
    tag = tag_factory.create(name='Test Tag')
    url = reverse('tag-detail', kwargs={'slug': tag.slug})

    post_factory.create_batch(size=2, tags=[tag])

    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']
    assert response_data['data']['included']


def test_get_tag_not_found(db, client):
    url = reverse('tag-detail', kwargs={'slug': 'non-existing-slug'})

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='No Tag matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_get_single_tag_server_error(
    db, client, tag_factory, monkeypatch, fake_method_factory
):
    tag = tag_factory.create()
    url = reverse('tag-detail', kwargs={'slug': tag.slug})

    monkeypatch.setattr(
        'apps.content.views.tags.get_object_or_404',
        fake_method_factory(raise_exception=Exception('Database connection failed')),
    )

    response = client.get(url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Database connection failed',
        status=500,
        title='Internal Server Error',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')
