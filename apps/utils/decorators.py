from functools import wraps

from django.http import JsonResponse


def roles_required(allowed_roles: list[str], func: callable):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if getattr(request.user, 'role', None) not in allowed_roles:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        return func(request, *args, **kwargs)

    return wrapper


def admin_required(func: callable):
    return roles_required(['admin'], func)


def admin_or_author_required(func: callable):
    return roles_required(['admin', 'author'], func)


def login_required(func: callable):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return func(request, *args, **kwargs)

    return wrapper


def require_http_methods_json_response(allowed_methods: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method not in allowed_methods:
                return JsonResponse(
                    {'error': 'Method not allowed'},
                    status=405,
                    content_type='application/vnd.api+json',
                )
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
