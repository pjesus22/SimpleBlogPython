from django.urls import reverse


def test_get_post_media(db, client, post_factory, media_file_factory):
    post = post_factory.create()
    media_file_factory.create_batch(3, post=post)

    url = reverse('post-media-list', kwargs={'slug': post.slug})
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.json()['data']) == 3


def test_get_post_media_post_not_found(db, client):
    url = reverse('post-media-list', kwargs={'slug': 'not-found'})
    response = client.get(url)
    assert response.status_code == 404
    assert response.json()['error'] == 'Post not found'


def test_get_post_media_item(db, client, post_factory, media_file_factory):
    post = post_factory.create()
    media_file = media_file_factory.create(post=post)

    url = reverse(
        'post-media-detail', kwargs={'slug': post.slug, 'id': str(media_file.id)}
    )
    response = client.get(url)
    assert response.status_code == 200


def test_get_post_media_item_not_found(db, client, post_factory):
    post = post_factory.create()
    url = reverse('post-media-detail', kwargs={'slug': post.slug, 'id': '1000'})
    response = client.get(url)
    assert response.status_code == 404
    assert response.json()['error'] == 'Media file item not found'
