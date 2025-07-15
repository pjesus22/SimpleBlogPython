from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_get_category_list(db, client, category_factory):
    url = reverse('category-list')

    category_factory.create_batch(size=2)

    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']
    assert len(response_data['data']) == 2


def test_get_category_list_server_error(db, monkeypatch, client, fake_method_factory):
    url = reverse('category-list')

    monkeypatch.setattr(
        'apps.content.views.categories.Category.objects.all',
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


def test_get_single_category(db, client, category_factory, post_factory):
    category = category_factory.create(
        name='Test Category', description='fake category description'
    )
    url = reverse('category-detail', kwargs={'slug': category.slug})

    post_factory.create_batch(size=2, category=category)

    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']
    assert response_data['data']['included']


def test_get_category_not_found(db, client):
    url = reverse('category-detail', kwargs={'slug': 'non-existing-slug'})

    response = client.get(url)
    response_data = response.json()

    expected_response = build_expected_error(
        detail='No Category matches the given query.',
        status=404,
        title='Not Found',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected_response in response_data.get('errors')


def test_get_single_category_server_error(
    db, client, category_factory, monkeypatch, fake_method_factory
):
    category = category_factory.create()
    url = reverse('category-detail', kwargs={'slug': category.slug})

    monkeypatch.setattr(
        'apps.content.views.categories.get_object_or_404',
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
