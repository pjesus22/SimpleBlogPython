import json

from django.urls import reverse

from apps.content.models import Tag
from tests.unit_tests.api.conftest import build_expected_error


def test_delete_tag_success(db, logged_admin_client, tag):
    url = reverse('tag-detail', kwargs={'slug': tag.slug})

    response = logged_admin_client.delete(path=url)

    assert response.status_code == 204
    assert not Tag.objects.filter(slug=tag.slug).exists()


def test_delete_tag_not_found(db, logged_admin_client):
    url = reverse('tag-detail', kwargs={'slug': 'non-existing-slug'})

    response = logged_admin_client.delete(path=url)

    assert response.status_code == 404


def test_delete_tag_generic_exception(
    db, logged_admin_client, monkeypatch, fake_method_factory, tag_factory
):
    tag_factory.create(name='Test Tag')

    url = reverse('tag-detail', kwargs={'slug': 'test-tag'})

    monkeypatch.setattr(
        'apps.content.views.tags.Tag.delete',
        fake_method_factory(raise_exception=Exception('Something went wrong')),
    )

    response = logged_admin_client.delete(
        path=url, data=json.dumps({'name': 'test tag'})
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data.get('errors')
