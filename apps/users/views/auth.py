import json

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.middleware.csrf import get_token

from apps.utils.decorators import require_http_methods_json_response
from apps.utils.jsonapi_responses import JsonApiResponseBuilder as jarb
from apps.utils.validators import validate_invalid_fields, validate_required_fields


@require_http_methods_json_response(['POST'])
def login_view(request):
    try:
        data = json.loads(request.body)

        validate_invalid_fields(data, allowed_fields={'username', 'password'})
        validate_required_fields(data, required_fields={'username', 'password'})

        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return jarb.ok(
                {'message': f'Successfully logged in with user id {user.id}'}
            )
        else:
            return jarb.error(401, 'Unauthorized', 'Invalid username or password.')

    except json.JSONDecodeError:
        return jarb.error(400, 'Bad Request', 'Invalid JSON format.')
    except ValidationError as e:
        return jarb.validation_errors_from_dict(e.message_dict)
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
