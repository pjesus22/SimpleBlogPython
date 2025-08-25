import json

import pytest
from django.http import JsonResponse
from django.test import RequestFactory

from apps.utils.decorators import (
    admin_or_author_required,
    admin_required,
    login_required,
    require_http_methods_json_response,
    roles_required,
)


@pytest.fixture
def rf():
    return RequestFactory()


def dummy_view(request):
    return JsonResponse({'success': True})


class DummyUser:
    def __init__(self, role=None, is_authenticated=True):
        self.role = role
        self.is_authenticated = is_authenticated


@pytest.mark.parametrize(
    'user_role,allowed_roles,expected_status,expected_success',
    [
        ('admin', ['admin'], 200, True),
        ('author', ['admin'], 403, False),
        ('author', ['author', 'admin'], 200, True),
        ('None', ['admin'], 403, False),
    ],
)
def test_roles_required(
    rf, user_role, allowed_roles, expected_status, expected_success
):
    request = rf.get('/fake-url/')
    request.user = DummyUser(role=user_role, is_authenticated=True)

    decorated_view = roles_required(allowed_roles, dummy_view)
    response = decorated_view(request)
    response_data = json.loads(response.content.decode())

    assert response.status_code == expected_status

    if expected_success:
        assert response_data.get('success') is True
    else:
        assert 'errors' in response_data
        assert response_data['errors'][0]['status'] == str(expected_status)
        assert response_data['errors'][0]['title'] == 'Forbidden'


def test_admin_required_success(rf):
    request = rf.get('/fake-url/')
    request.user = DummyUser(role='admin', is_authenticated=True)

    decorated_view = admin_required(dummy_view)
    response = decorated_view(request)
    response_data = json.loads(response.content.decode())

    assert response.status_code == 200
    assert response_data.get('success') is True


@pytest.mark.parametrize('user_role', [('admin'), ('author')])
def test_admin_or_author_required_success(rf, user_role):
    request = rf.get('/fake-url/')
    request.user = DummyUser(role=user_role, is_authenticated=True)

    decorated_view = admin_or_author_required(dummy_view)
    response = decorated_view(request)
    response_data = json.loads(response.content.decode())

    assert response.status_code == 200
    assert response_data.get('success') is True


@pytest.mark.parametrize('authenticated', [True, False])
def test_login_required(rf, authenticated):
    request = rf.get('/fake-url/')
    request.user = DummyUser(role='admin', is_authenticated=authenticated)

    decorated_view = login_required(dummy_view)
    response = decorated_view(request)
    response_data = json.loads(response.content.decode())

    if authenticated:
        assert response.status_code == 200
        assert response_data.get('success') is True
    else:
        errors = response_data['errors'][0]
        assert response.status_code == 401
        assert errors['status'] == '401'
        assert errors['title'] == 'Unauthorized'
        assert errors['detail'] == (
            'User must be authenticated to access this resource.'
        )
        assert 'meta' in errors


@pytest.mark.parametrize('method', [['GET'], ['POST']])
def test_require_http_methods_json_response_allows_method(rf, method):
    request = rf.get('/fake-url/')
    request.user = DummyUser(role='admin', is_authenticated=True)

    decorated_view = require_http_methods_json_response(allowed_methods=method)(
        dummy_view
    )
    response = decorated_view(request)
    response_data = json.loads(response.content.decode())

    if method[0] == 'GET':
        assert response.status_code == 200
        assert response_data.get('success') is True
    else:
        errors = response_data['errors'][0]
        assert response.status_code == 405
        assert errors['status'] == '405'
        assert errors['title'] == 'Method Not Allowed'
        assert errors['detail'] == (
            f'Method {request.method} is not allowed for this endpoint.'
        )
        assert 'meta' in errors
