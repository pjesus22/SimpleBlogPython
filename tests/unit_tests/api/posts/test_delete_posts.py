from django.urls import reverse

from apps.content.models.posts import Post


def test_delete_post_success(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 204


def test_delete_post_not_found(db, logged_admin_client):
    url = reverse('post-detail', kwargs={'slug': 'non-existing-slug'})
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 404


def test_delete_post_do_not_have_permission(db, logged_author_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    response = logged_author_client.delete(path=url)

    assert response.status_code == 403


def test_delete_post_generic_exception(db, logged_admin_client, post_factory, override):
    def fake_delete(*args, **kwargs):
        raise Exception('Something went wrong')

    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})

    with override(Post, 'delete', fake_delete):
        response = logged_admin_client.delete(path=url)

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']
