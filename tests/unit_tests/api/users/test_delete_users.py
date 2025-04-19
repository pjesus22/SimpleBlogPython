import pytest
from django.urls import reverse

from apps.users.models import User


@pytest.fixture
def test_author(db, author_factory):
    return author_factory()


def test_delete_user_success(db, logged_admin_client, test_author):
    url = reverse('user-detail', kwargs={'pk': test_author.pk})
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 204


def test_delete_user_not_found(db, logged_admin_client):
    url = reverse('user-detail', kwargs={'pk': 1000})
    response = logged_admin_client.delete(path=url)

    assert response.status_code == 404
    assert response.json()['error'] == 'User not found'


def test_delete_user_category_generic_exception(
    db, logged_admin_client, override, test_author
):
    def fake_delete(*args, **kwargs):
        raise Exception('Something went wrong')

    with override(User, 'delete', fake_delete):
        url = reverse('user-detail', kwargs={'pk': test_author.pk})
        response = logged_admin_client.delete(path=url)

    assert response.status_code == 500
    assert 'Something went wrong' in response.json()['error']


def test_delete_user_does_not_have_permission(db, logged_author_client, test_author):
    url = reverse('user-detail', kwargs={'pk': test_author.pk})
    response = logged_author_client.delete(url, content_type='application/json')

    assert response.status_code == 403
    assert response.json()['error'] == 'Permission denied'
