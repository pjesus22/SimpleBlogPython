from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_post_social_account_success(db, logged_author_client):
    url = reverse('social-account-list', kwargs={'user_id': 1})
    payload = {
        'provider': 'facebook',
        'username': 'user.name1234',
        'url': 'https://www.facebook.com/user.name1234',
    }

    response = logged_author_client.post(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    assert response.status_code == 201
    assert response_data['data']
    assert response_data['data']['relationships']


def test_post_social_account_unauthorized(db, logged_author_client, author_factory):
    user = author_factory.create()
    url = reverse('social-account-list', kwargs={'user_id': user.id})
    payload = {
        'provider': 'facebook',
        'username': 'user.name1234',
        'url': 'https://www.facebook.com/user.name1234',
    }

    response = logged_author_client.post(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Permission denied', status=403, meta=response_data['errors'][0]['meta']
    )

    assert response.status_code == 403
    assert expected in response_data['errors']


def test_post_social_account_invalid_json(db, logged_author_client, author_factory):
    url = reverse('social-account-list', kwargs={'user_id': 1})
    payload = "'{invalid json"

    response = logged_author_client.post(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Invalid JSON: Expecting value: line 1 column 1 (char 0)',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_post_social_account_validation_error(db, logged_author_client, author_factory):
    url = reverse('social-account-list', kwargs={'user_id': 1})
    payload = {
        'provider': 'facebook',
        'username': 'user.name1234',
        'url': 'hts://.com/user.name1234',
    }

    response = logged_author_client.post(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Enter a valid URL.',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_post_social_account_profile_not_found(db, logged_admin_client):
    url = reverse('social-account-list', kwargs={'user_id': 9999})
    payload = {
        'provider': 'facebook',
        'username': 'user.name1234',
        'url': 'https://www.facebook.com/user.name1234',
    }
    response = logged_admin_client.post(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='No AuthorProfile matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data['errors']


def test_post_social_account_generic_error(
    db, logged_author_client, monkeypatch, fake_method_factory
):
    url = reverse('social-account-list', kwargs={'user_id': 1})
    payload = {
        'provider': 'facebook',
        'username': 'user.name1234',
        'url': 'https://www.facebook.com/user.name1234',
    }

    monkeypatch.setattr(
        'apps.users.views.author_profiles.SocialAccount.save',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_author_client.post(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong.',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data['errors']
