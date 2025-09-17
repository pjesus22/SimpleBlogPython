from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_patch_author_profile_success(db, logged_admin_client, author_factory):
    user = author_factory.create()
    url = reverse('author-profile-detail', kwargs={'user_id': user.id})
    payload = {'bio': 'New biography text'}

    response = logged_admin_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']['attributes']['bio'] == 'New biography text'


def test_patch_author_profile_unauthorized(db, logged_author_client, author_factory):
    user = author_factory.create()
    url = reverse('author-profile-detail', kwargs={'user_id': user.id})
    payload = {'bio': 'New biography text'}

    response = logged_author_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Permission denied',
        status=403,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data['errors']


def test_patch_author_profile_invalid_json(db, logged_admin_client, author_factory):
    user = author_factory.create()
    url = reverse('author-profile-detail', kwargs={'user_id': user.id})
    payload = "'{invalid json"

    response = logged_admin_client.patch(path=url, data=payload)
    response_data = response.json()

    print(response_data)

    expected = build_expected_error(
        detail='Expecting value: line 1 column 1 (char 0)',
        status=400,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_patch_author_profile_validation_error(db, logged_admin_client, author_factory):
    user = author_factory.create()
    url = reverse('author-profile-detail', kwargs={'user_id': user.id})
    payload = {'invalid_field': 'Some value'}

    response = logged_admin_client.patch(
        path=url,
        data=payload,
        content_type='application/json',
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='This field is not allowed.', meta=response_data['errors'][0]['meta']
    )

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_patch_author_profile_not_found(db, logged_admin_client, author_factory):
    url = reverse('author-profile-detail', kwargs={'user_id': '1000'})
    payload = {'bio': 'Some value'}

    response = logged_admin_client.patch(
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


def test_patch_author_profile_generic_error(
    db, logged_admin_client, author_factory, monkeypatch, fake_method_factory
):
    user = author_factory.create()
    url = reverse('author-profile-detail', kwargs={'user_id': user.id})
    payload = {'bio': 'Some value'}

    monkeypatch.setattr(
        'apps.users.views.author_profiles.AuthorProfile.save',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = logged_admin_client.patch(
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
