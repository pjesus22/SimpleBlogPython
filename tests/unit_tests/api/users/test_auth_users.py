from django.urls import reverse

from tests.unit_tests.api.conftest import build_expected_error


def test_csrf_token_view(csrf_client):
    url = reverse('csrf-token')

    response = csrf_client.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']['csrfToken']


def test_login_success(db, csrf_client, author_factory):
    user = author_factory.create(username='test_user')
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = {'username': user.username, 'password': 'password'}

    response = csrf_client.post(
        url, data=payload, content_type='application/json', HTTP_X_CSRFTOKEN=csrf_token
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']['message'] == 'Successfully logged in with user id 1'


def test_login_missing_fields(csrf_client):
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = {'username': 'testuser'}

    response = csrf_client.post(
        url, data=payload, content_type='application/json', HTTP_X_CSRFTOKEN=csrf_token
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='This field is required.',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_login_invalid_credentials(db, csrf_client, author_factory):
    user = author_factory(username='test_user')
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = {'username': user.username, 'password': 'wrong_password'}

    response = csrf_client.post(
        url, data=payload, content_type='application/json', HTTP_X_CSRFTOKEN=csrf_token
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Invalid username or password.',
        status=401,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 401
    assert expected in response_data['errors']


def test_login_invalid_fields(csrf_client):
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = {'username': 'testuser', 'password': 'password', 'invalid': 'invalid'}

    response = csrf_client.post(
        url, data=payload, content_type='application/json', HTTP_X_CSRFTOKEN=csrf_token
    )
    response_data = response.json()

    print(response_data)

    expected = build_expected_error(
        detail='This field is not allowed.',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_login_json_decode_error(csrf_client):
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = "'{invalid json"

    response = csrf_client.post(
        url, data=payload, content_type='application/json', HTTP_X_CSRFTOKEN=csrf_token
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Invalid JSON format.',
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_login_generic_exception(
    db, csrf_client, monkeypatch, fake_method_factory, author_factory
):
    url = reverse('login')
    csrf_token = csrf_client.get(reverse('csrf-token')).cookies['csrftoken'].value
    payload = {'username': 'test_user', 'password': 'password'}

    author_factory(username='test_user')

    monkeypatch.setattr(
        'apps.users.views.auth.authenticate',
        fake_method_factory(raise_exception=Exception('Something went wrong.')),
    )

    response = csrf_client.post(
        url, data=payload, content_type='application/json', HTTP_X_CSRFTOKEN=csrf_token
    )
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong.',
        status=500,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 500
    assert expected in response_data['errors']


def test_logout_success(db, logged_author_client):
    url = reverse('logout')

    response = logged_author_client.post(url, content_type='application/json')
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']['message'] == 'Successfully logged out'


def test_logout_without_authentication(client):
    response = client.post(reverse('logout'))
    response_data = response.json()

    expected = build_expected_error(
        detail='User is not authenticated',
        status=403,
        meta=response_data['errors'][0]['meta'],
    )

    assert response.status_code == 403
    assert expected in response_data['errors']
