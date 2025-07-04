import json

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.test import RequestFactory

from apps.utils.decorators import (
    admin_or_author_required,
    admin_required,
    login_required,
    require_http_methods_json_response,
    roles_required,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def rf():
    return RequestFactory()


def mock_get_view(request):
    return JsonResponse({'success': True}, status=200)


@pytest.mark.parametrize(
    'user, expected_status', [('valid_user', 200), ('anon_user', 401)]
)
def test_login_required_decorator(rf, author_factory, user, expected_status):
    request = rf.get('/fake-url/')
    match user:
        case 'valid_user':
            request.user = author_factory()
        case 'anon_user':
            request.user = AnonymousUser()

    decorator_view = login_required(mock_get_view)
    response = decorator_view(request)

    response_data = json.loads(response.content.decode())

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response_data.get('success')
    else:
        assert {
            'status': '401',
            'title': 'Unauthorized',
            'detail': 'User must be authenticated to access this resource.',
        } in response_data['errors']


@pytest.mark.parametrize(
    'user_fixture, decorator',
    [
        ('author_factory', 'roles_required'),
        ('admin_factory', 'roles_required'),
        ('admin_factory', 'admin_required'),
        ('admin_factory', 'admin_or_author_required'),
        ('author_factory', 'admin_or_author_required'),
    ],
)
def test_role_required_decorator(
    rf, author_factory, admin_factory, user_fixture, decorator
):
    request = rf.get('/fake-url/')

    match user_fixture:
        case 'author_factory':
            request.user = author_factory.create()
        case 'admin_factory':
            request.user = admin_factory.create()

    match decorator:
        case 'roles_required':
            decorator_view = roles_required(['admin'], mock_get_view)
        case 'admin_or_author_required':
            decorator_view = admin_or_author_required(mock_get_view)
        case 'admin_required':
            decorator_view = admin_required(mock_get_view)

    response = decorator_view(request)
    response_data = json.loads(response.content.decode())

    if decorator == 'roles_required' and request.user.role == 'author':
        expected_error = {
            'status': '403',
            'title': 'Forbidden',
            'detail': 'User does not have permission to access this resource.',
        }

        assert response.status_code == 403
        assert expected_error in response_data.get('errors', [])
    else:
        assert response.status_code == 200
        assert response_data.get('success')


@pytest.mark.parametrize(
    'method, expected_status, expected_detail',
    [
        ('GET', 200, None),
        ('POST', 405, 'Method POST is not allowed for this endpoint.'),
    ],
)
def test_require_http_methods_json_response_decorator(
    rf, method, expected_status, expected_detail
):
    request_method = getattr(rf, method.lower())
    request = request_method('/fake-url/')

    decorator_view = require_http_methods_json_response(['GET'])(mock_get_view)
    response = decorator_view(request)

    response_data = json.loads(response.content.decode())

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response_data.get('success')
    else:
        assert {
            'status': '405',
            'title': 'Method Not Allowed',
            'detail': expected_detail,
        } in response_data['errors']
