from django.urls import reverse

from apps.users.models import AuthorProfile
from tests.unit_tests.api.conftest import build_expected_error


def test_update_social_accounts_success(
    db,
    logged_author_client,
    social_account_factory,
):
    profile = AuthorProfile.objects.all().first()
    social_account = social_account_factory.create(profile=profile)
    url = reverse(
        viewname='social-account-detail',
        kwargs={'user_id': profile.user.id, 'social_id': social_account.id},
    )
    payload = {
        'provider': 'twitter',
        'username': 'new_username',
        'url': 'https://www.twitter.com/new_username',
    }

    response = logged_author_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']['attributes']['provider'] == 'twitter'
    assert response_data['data']['attributes']['username'] == 'new_username'
    assert (
        response_data['data']['attributes']['url']
        == 'https://www.twitter.com/new_username'
    )


def test_update_social_accounts_unauthorized(
    db, logged_author_client, social_account_factory, author_factory
):
    user = author_factory.create()
    profile = user.profile
    social_account = social_account_factory.create(profile=profile)
    url = reverse(
        viewname='social-account-detail',
        kwargs={'user_id': user.id, 'social_id': social_account.id},
    )
    payload = {
        'provider': 'twitter',
        'username': 'new_username',
        'url': 'https://www.twitter.com/new_username',
    }

    response = logged_author_client.patch(
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


def test_update_social_accounts_invalid_json(
    db, logged_author_client, social_account_factory
):
    profile = AuthorProfile.objects.all().first()
    social_account = social_account_factory.create(profile=profile)
    url = reverse(
        viewname='social-account-detail',
        kwargs={'user_id': profile.user.id, 'social_id': social_account.id},
    )
    payload = "'{invalid json"

    response = logged_author_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Invalid JSON: Expecting value: line 1 column 1 (char 0)',
        status=400,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_update_social_accounts_validation_error(
    db, logged_author_client, social_account_factory
):
    profile = AuthorProfile.objects.all().first()
    social_account = social_account_factory.create(profile=profile)
    url = reverse(
        viewname='social-account-detail',
        kwargs={'user_id': profile.user.id, 'social_id': social_account.id},
    )
    payload = {'invalid_field': 'some value'}

    response = logged_author_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='This field is not allowed.',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_update_social_accounts_not_found(
    db, logged_author_client, social_account_factory
):
    url = reverse(
        viewname='social-account-detail',
        kwargs={'user_id': 1, 'social_id': 9999},
    )
    payload = {
        'provider': 'twitter',
        'username': 'new_username',
        'url': 'https://www.twitter.com/new_username',
    }

    response = logged_author_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='No SocialAccount matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data['errors']


def test_update_social_accounts_generic_error(
    db, logged_author_client, social_account_factory, monkeypatch, fake_method_factory
):
    profile = AuthorProfile.objects.all().first()
    social_account = social_account_factory.create(profile=profile)
    url = reverse(
        viewname='social-account-detail',
        kwargs={'user_id': profile.user.id, 'social_id': social_account.id},
    )
    payload = {
        'provider': 'twitter',
        'username': 'new_username',
        'url': 'https://www.twitter.com/new_username',
    }

    monkeypatch.setattr(
        'apps.users.views.author_profiles.SocialAccount.save',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_author_client.patch(
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
