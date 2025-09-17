from django.urls import reverse

from apps.users.models import AuthorProfile
from tests.unit_tests.api.conftest import build_expected_error


def test_delete_social_accounts_success(
    db, logged_author_client, social_account_factory
):
    profile = AuthorProfile.objects.all().first()
    social_account = social_account_factory.create(profile=profile)
    url = reverse(
        viewname='social-account-detail',
        kwargs={'user_id': profile.user.id, 'social_id': social_account.id},
    )

    response = logged_author_client.delete(path=url)

    assert response.status_code == 204
    assert not profile.social_accounts.filter(id=social_account.id).exists()


def test_delete_social_accounts_unauthorized(
    db, logged_author_client, social_account_factory, author_factory
):
    user = author_factory.create()
    profile = user.profile
    social_account = social_account_factory.create(profile=profile)
    url = reverse(
        viewname='social-account-detail',
        kwargs={'user_id': user.id, 'social_id': social_account.id},
    )

    response = logged_author_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Permission denied', status=403, meta=response_data['errors'][0]['meta']
    )

    assert response.status_code == 403
    assert expected in response_data['errors']


def test_delete_social_accounts_not_found(
    db, logged_author_client, social_account_factory, author_factory
):
    profile = AuthorProfile.objects.all().first()
    url = reverse(
        viewname='social-account-detail',
        kwargs={'user_id': profile.user.id, 'social_id': 9999},
    )

    social_account_factory.create(profile=profile)

    response = logged_author_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        detail='No SocialAccount matches the given query.',
        status=404,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 404
    assert expected in response_data['errors']


def test_delete_social_accounts_generic_error(
    db, logged_author_client, social_account_factory, monkeypatch, fake_method_factory
):
    profile = AuthorProfile.objects.all().first()
    social_account = social_account_factory.create(profile=profile)
    url = reverse(
        viewname='social-account-detail',
        kwargs={'user_id': profile.user.id, 'social_id': social_account.id},
    )

    monkeypatch.setattr(
        'apps.users.views.author_profiles.SocialAccount.delete',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_author_client.delete(path=url)
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong.',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data['errors']
