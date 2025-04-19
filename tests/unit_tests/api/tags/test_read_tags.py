from django.urls import reverse


def test_get_tags(db, client, tag_factory):
    tag_factory.create_batch(size=3)

    url = reverse('tag-list')
    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert len(response_data['data']) == 3


def test_get_tag(db, client, tag_factory, post_factory):
    tag = tag_factory.create(name='test tag')

    post_factory.create_batch(size=3, tags=[tag])

    url = reverse('tag-detail', kwargs={'slug': tag.slug})
    response = client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert 'data' in response_data
    assert 'included' in response_data


def test_get_tag_not_found(db, client):
    url = reverse('tag-detail', kwargs={'slug': 'non-existing-slug'})
    response = client.get(url)
    expected_response = {'error': 'Tag not found'}

    assert response.status_code == 404
    assert response.json() == expected_response
