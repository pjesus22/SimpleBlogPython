from django.urls import reverse


def fake_method(*args, **kwargs):
    raise Exception('Database connection failed')


def test_get_category_list(db, client, category_factory):
    category_factory.create_batch(size=2)

    url = reverse('category-list')
    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']
    assert len(response_data['data']) == 2


def test_get_category_list_server_error(db, monkeypatch, client, override):
    target = 'apps.content.views.categories.Category.objects.all'
    monkeypatch.setattr(target, fake_method)
    url = reverse('category-list')
    response = client.get(url)
    response_data = response.json()

    expected = {
        'status': '500',
        'title': 'Internal Server Error',
        'detail': 'Database connection failed',
        'meta': response_data['errors'][0]['meta'],
    }

    assert response.status_code == 500
    assert expected in response_data['errors']


def test_get_single_category(db, client, category_factory, post_factory):
    category = category_factory.create(
        name='test category', description='fake category description'
    )
    post_factory.create_batch(size=2, category=category)

    url = reverse('category-detail', kwargs={'slug': category.slug})
    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']
    assert response_data['data']['included']


def test_get_category_not_found(db, client):
    url = reverse('category-detail', kwargs={'slug': 'non-existing-slug'})
    response = client.get(url)
    response_data = response.json()
    expected_response = {
        'status': '404',
        'title': 'Not Found',
        'detail': 'No Category matches the given query.',
        'meta': response_data['errors'][0]['meta'],
    }

    assert response.status_code == 404
    assert expected_response in response_data['errors']


def test_get_single_category_server_error(db, client, category_factory, monkeypatch):
    category = category_factory.create()

    def fake_get(*args, **kwargs):
        raise Exception('Database connection failed')

    monkeypatch.setattr('apps.content.views.categories.get_object_or_404', fake_get)

    url = reverse('category-detail', kwargs={'slug': category.slug})
    response = client.get(url)
    response_data = response.json()

    expected = {
        'status': '500',
        'title': 'Internal Server Error',
        'detail': 'Database connection failed',
        'meta': response_data['errors'][0]['meta'],
    }

    assert response.status_code == 500
    assert expected in response_data['errors']
