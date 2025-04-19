from django.urls import reverse


def test_get_posts(db, client, post_factory):
    post_factory.create_batch(3)
    url = reverse('post-list')
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.json()['data']) == 3


def test_get_posts_by_category(db, client, post_factory, category_factory):
    category = category_factory.create()
    post_factory.create_batch(2, category=category)
    post_factory.create_batch(1)
    url = reverse('post-list')
    response = client.get(url, {'category': category.slug})

    assert response.status_code == 200
    assert len(response.json()['data']) == 2


def test_get_posts_by_tags(db, client, post_factory, tag_factory):
    tags = tag_factory.create_batch(2)
    post_factory.create_batch(2, tags=tags)
    post_factory.create_batch(2)

    url = reverse('post-list')
    response = client.get(url, {'tags': f'{tags[0].name},{tags[1].name}'})

    assert response.status_code == 200
    assert len(response.json()['data']) == 2


def test_get_posts_by_search(db, client, post_factory):
    post_factory.create_batch(3)
    post_factory.create(title='Lorem ipsum dolor sit amet')
    url = reverse('post-list')
    response = client.get(url, {'search': 'dolor'})

    assert response.status_code == 200
    assert len(response.json()['data']) == 1


def test_get_post(db, client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    response = client.get(url)

    assert response.status_code == 200
    assert response.json()['data']['id'] == str(post.id)


def test_get_post_not_found(db, client, post_factory):
    url = reverse('post-detail', kwargs={'slug': 'not-found'})
    response = client.get(url)

    assert response.status_code == 404
    assert response.json()['error'] == 'Post not found'
