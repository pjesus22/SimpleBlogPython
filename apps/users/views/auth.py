import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token

from apps.utils.decorators import require_http_methods_json_response


@require_http_methods_json_response(['POST'])
def login_view(request):
    try:
        data = json.loads(request.body)
        allowed_fields = {'username', 'password'}
        invalid_fields = set(data) - allowed_fields

        if invalid_fields:
            return JsonResponse(
                {'error': f'Invalid fields: {", ".join(invalid_fields)}'},
                status=400,
            )

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse(
                {'error': 'Both username and password are required'}, status=400
            )

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return JsonResponse(
                {'message': 'Successfully logged in', 'user': user.username}
            )
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods_json_response(['POST'])
def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No authenticated user'}, status=401)

    logout(request)
    return JsonResponse({'message': 'Successfully logged out'})


@require_http_methods_json_response(['GET'])
def csrf_token_view(request):
    return JsonResponse({'token': get_token(request)})
