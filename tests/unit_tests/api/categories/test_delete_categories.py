from django.urls import reverse

from apps.content.models import Category


def test_delete_category_success(db, logged_admin_client, category_factory):
    category = category_factory.create()
    url = reverse('category-detail', kwargs={'slug': category.slug})

    response = logged_admin_client.delete(path=url)
    assert response.status_code == 204
    assert not Category.objects.filter(slug=category.slug).exists()


def test_delete_category_not_found(db, logged_admin_client):
    url = reverse('category-detail', kwargs={'slug': 'non-existing-slug'})
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 404


def test_delete_category_generic_exception(
    db, monkeypatch, logged_admin_client, category_factory
):
    category = category_factory.create()

    def fake_delete(*args, **kwargs):
        raise Exception('Something went wrong')

    monkeypatch.setattr('apps.content.views.categories.Category.delete', fake_delete)

    response = logged_admin_client.delete(
        path=reverse('category-detail', kwargs={'slug': category.slug})
    )

    response_data = response.json()

    expected = {
        'status': '500',
        'title': 'Internal Server Error',
        'detail': 'Something went wrong',
        'meta': response_data['errors'][0]['meta'],
    }

    assert response.status_code == 500
    assert expected in response_data['errors']
