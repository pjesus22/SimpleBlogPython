from django.urls import reverse


def test_get_categories(db, client, category_factory):
    category_factory.create_batch(size=3)

    url = reverse('category-list')
    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert len(response_data['data']) == 3


def test_get_category(db, client, category_factory, post_factory):
    category = category_factory.create(
        name='test category', description='fake category description'
    )

    post_factory.create_batch(size=3, category=category)

    url = reverse('category-detail', kwargs={'slug': category.slug})
    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert 'included' in response_data


def test_get_category_not_found(db, client):
    url = reverse('category-detail', kwargs={'slug': 'non-existing-slug'})
    response = client.get(url)
    expected_response = {'error': 'Category not found'}

    assert response.status_code == 404
    assert response.json() == expected_response
