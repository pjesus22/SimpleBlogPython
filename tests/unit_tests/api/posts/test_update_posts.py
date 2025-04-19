from django.urls import reverse

from apps.content.models.posts import Post


def test_patch_post_success(
    db, logged_admin_client, post_factory, category_factory, tag_factory
):
    post = post_factory.create()
    new_category = category_factory.create()
    new_tags = tag_factory.create_batch(2)
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {
        'content': 'updated content',
        'category': new_category.slug,
        'tags': [f'{tag.slug}' for tag in new_tags],
    }
    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )

    assert response.status_code == 200
    assert response.json()['data']['attributes']['content'] == payload['content']


def test_patch_post_not_found(db, logged_admin_client):
    url = reverse('post-detail', kwargs={'slug': 'not-found'})
    payload = {'content': 'updated content'}
    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )

    assert response.status_code == 404
    assert response.json()['error'] == 'Post not found'


def test_patch_do_not_have_permission(
    db, logged_author_client, post_factory, author_factory
):
    user = author_factory.create(username='testuser')
    post = post_factory.create(author=user)
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'content': 'updated content'}
    response = logged_author_client.patch(
        path=url, data=payload, content_type='application/json'
    )

    assert response.status_code == 403
    assert response.json()['error'] == 'Permission denied'


def test_patch_post_invalid_fields(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'content': 'updated content', 'invalid': 'invalid'}
    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid fields: invalid'


def test_patch_post_category_not_found(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'category': 'invalid-category'}
    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )

    assert response.status_code == 404
    assert response.json()['error'] == 'Category not found'


def test_patch_post_tag_not_found(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'tags': ['invalid-tag']}
    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )

    assert response.status_code == 404
    assert response.json()['error'] == 'Tag not found: invalid-tag'


def test_patch_post_json_decode_error(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = "'{invalid json"

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'Expecting value'


def test_patch_post_validation_error(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {
        'title': (
            'Lorem ipsum dolor sit amet, consectetuer '
            'adipiscing elit. Aenean commodo ligula eget dolor.'
        )
    }

    response = logged_admin_client.patch(
        path=url, data=payload, content_type='application/json'
    )

    assert response.status_code == 400
    assert 'title' in response.json()['error']


def test_patch_post_generic_exception(db, logged_admin_client, override, post_factory):
    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    payload = {'content': 'updated content'}

    with override(Post, 'save', fake_save):
        response = logged_admin_client.patch(
            path=url, data=payload, content_type='application/json'
        )

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
