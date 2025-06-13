from functools import wraps

from .jsonapi_responses import JsonApiResponseBuilder as jarb


def roles_required(allowed_roles: list[str], func: callable):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if getattr(request.user, 'role', None) not in allowed_roles:
            return jarb.error(
                403,
                'Forbidden',
                'User does not have permission to access this resource.',
            )
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
            return jarb.error(
                401,
                'Unauthorized',
                'User must be authenticated to access this resource.',
            )
        return func(request, *args, **kwargs)

    return wrapper


def require_http_methods_json_response(allowed_methods: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method not in allowed_methods:
                return jarb.error(
                    405,
                    'Method Not Allowed',
                    f'Method {request.method} is not allowed for this endpoint.',
                )
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
