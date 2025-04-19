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
def mock_request():
    return RequestFactory().get('/fake-url/')


@pytest.fixture
def json_response():
    def _parse(response):
        return json.loads(response.content.decode('utf-8'))

    return _parse


def dummy_view(request):
    return JsonResponse({'success': True})


def test_login_required_success(mock_request, author_factory, json_response):
    mock_request.user = author_factory.create()

    decorator_view = login_required(dummy_view)

    response = decorator_view(mock_request)
    data = json_response(response)

    assert response.status_code == 200
    assert data['success'] is True


def test_login_required_annonymous_user(mock_request, json_response):
    mock_request.user = AnonymousUser()

    decorator_view = login_required(dummy_view)

    response = decorator_view(mock_request)
    data = json_response(response)

    assert response.status_code == 401
    assert data['error'] == 'Authentication required'


def test_role_required_decorator_success(mock_request, author_factory, json_response):
    mock_request.user = author_factory.create()

    decorator_view = roles_required(['author'], dummy_view)

    response = decorator_view(mock_request)
    data = json_response(response)

    assert response.status_code == 200
    assert data['success'] is True


def test_role_required_decorator_unauthorized(
    mock_request, author_factory, json_response
):
    mock_request.user = author_factory.create()

    decorator_view = roles_required(['admin'], dummy_view)

    response = decorator_view(mock_request)
    data = json_response(response)

    assert response.status_code == 403
    assert data['error'] == 'Permission denied'


def test_admin_required_decorator_success(mock_request, admin_factory, json_response):
    mock_request.user = admin_factory.create()

    decorator_view = admin_required(dummy_view)

    response = decorator_view(mock_request)
    data = json_response(response)

    assert response.status_code == 200
    assert data['success'] is True


def test_admin_or_author_required_decorator_success(
    mock_request, author_factory, json_response
):
    mock_request.user = author_factory.create()

    decorator_view = admin_or_author_required(dummy_view)

    response = decorator_view(mock_request)
    data = json_response(response)

    assert response.status_code == 200
    assert data['success'] is True


def test_require_http_methods_json_response_allows_get(
    mock_request, author_factory, json_response
):
    @require_http_methods_json_response(['GET'])
    def dummy_get_view(request):
        return JsonResponse({'success': True})

    response = dummy_get_view(mock_request)
    data = json_response(response)

    assert response.status_code == 200
    assert data['success'] is True


def test_require_http_methods_json_response_blocks_post(author_factory, json_response):
    mock_post_request = RequestFactory().post('/fake-url/')

    response = require_http_methods_json_response(['GET'])(lambda request: ...)(
        mock_post_request
    )
    data = json_response(response)

    assert response.status_code == 405
    assert data['error'] == 'Method not allowed'
