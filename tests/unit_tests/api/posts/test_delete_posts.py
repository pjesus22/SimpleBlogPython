from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_delete_post_success(db, logged_admin_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 204


def test_delete_post_not_found(db, logged_admin_client):
    url = reverse('post-detail', kwargs={'slug': 'non-existing-slug'})

    response = logged_admin_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        detail='No Post matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data.get('errors')


def test_delete_post_do_not_have_permission(db, logged_author_client, post_factory):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})

    response = logged_author_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        detail='You do not have permission to delete this post',
        status=403,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data.get('errors')


def test_delete_post_generic_exception(
    db, logged_admin_client, post_factory, monkeypatch, fake_method_factory
):
    post = post_factory.create()
    url = reverse('post-detail', kwargs={'slug': post.slug})

    monkeypatch.setattr(
        'apps.content.views.posts.detail.Post.delete',
        fake_method_factory(raise_exception=Exception('Something went wrong')),
    )

    response = logged_admin_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')
