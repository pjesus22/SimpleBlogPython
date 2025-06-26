import json

from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token

from apps.utils.decorators import require_http_methods_json_response
from apps.utils.jsonapi_responses import JsonApiResponseBuilder as jarb


@require_http_methods_json_response(['POST'])
def login_view(request):
    try:
        data = json.loads(request.body)
        allowed_fields = {'username', 'password'}
        invalid_fields = set(data) - allowed_fields

        if invalid_fields:
            return jarb.error(
                400, 'Bad Request', f'Invalid fields: {", ".join(invalid_fields)}'
            )

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jarb.error(400, 'Bad Request', 'Username and password are required')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return jarb.ok(
                {
                    'message': f'Successfully logged in with user id {user.id}',
                }
            )
        else:
            return jarb.error(401, 'Unauthorized', 'Invalid username or password')

    except json.JSONDecodeError:
        return jarb.error(400, 'Bad Request', 'Invalid JSON format')
    except Exception as e:
        return jarb.error(500, 'Internal Server Error', str(e))


@require_http_methods_json_response(['POST'])
def logout_view(request):
    if not request.user.is_authenticated:
        return jarb.error(403, 'Forbidden', 'User is not authenticated')

    logout(request)
    return jarb.ok({'message': 'Successfully logged out'})


@require_http_methods_json_response(['GET'])
def csrf_token_view(request):
    return jarb.ok({'csrfToken': get_token(request)})
