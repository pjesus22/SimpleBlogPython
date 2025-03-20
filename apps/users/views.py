import json

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views import View

from apps.utils.permission_decorators import (
    admin_or_author_required,
    admin_required,
    login_required,
)

from .models import User
from .serializers import UserSerializer


class UserListView(View):
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return User.objects.all()

    @method_decorator([login_required, admin_required])
    def get(self, request, *args, **kwargs):
        response_data = {
            'data': [
                UserSerializer.serialize_user(user) for user in self.get_queryset()
            ]
        }
        return JsonResponse(response_data)

    @method_decorator([login_required, admin_required])
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            allowed_fields = {
                'username',
                'email',
                'password',
                'first_name',
                'last_name',
                'role',
            }
            if not set(data.keys()) <= allowed_fields:
                return JsonResponse(
                    {'error': f'Invalid fields: {", ".join(data.keys())}'},
                    status=400,
                )

            user = User(
                username=data.get('username'),
                email=data.get('email'),
                password=data.get('password'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                role=data.get('role'),
            )

            user.full_clean()
            user.save()
            return JsonResponse(UserSerializer.serialize_user(user), status=201)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': e.msg}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)


class UserDetailView(View):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_object(self):
        return User.objects.filter(username=self.kwargs.get('username')).first()

    @method_decorator([login_required, admin_or_author_required])
    def get(self, request, *args, **kwargs):
        user = self.get_object()

        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)

        if not (request.user.role == 'admin' or request.user.id == user.id):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        response_data = {'data': UserSerializer.serialize_user(user)}
        included = UserSerializer.build_included_data(user)

        if included:
            response_data['included'] = included

        return JsonResponse(response_data)

    @method_decorator([login_required, admin_or_author_required])
    def patch(self, request, *args, **kwargs):
        try:
            user = self.get_object()

            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)

            if not (request.user.role == 'admin' or request.user.id == user.id):
                return JsonResponse({'error': 'Permission denied'}, status=403)

            data = json.loads(request.body)
            allowed_fields = {
                'username',
                'email',
                'password',
                'first_name',
                'last_name',
            }
            invalid_fields = set(data) - allowed_fields

            if invalid_fields:
                return JsonResponse(
                    {'error': f'Invalid fields: {", ".join(invalid_fields)}'},
                    status=400,
                )

            for field in allowed_fields & data.keys():
                setattr(user, field, data[field])

            user.full_clean()
            user.save()
            return JsonResponse(UserSerializer.serialize_user(user), status=200)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': e.msg}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)

    @method_decorator([login_required, admin_required])
    def delete(self, request, *args, **kwargs):
        user = self.get_queryset()

        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)

        if not (request.user.role == 'admin' or request.user.id == user.id):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        user.delete()
        return HttpResponse(status=204)


def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        username = data['username']
        password = data['password']

        if not username or not password:
            return JsonResponse({'error': 'Missing username or password'}, status=400)

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return JsonResponse(
                {'message': 'Successfully logged in', 'user': user.username}
            )
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)


def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No authenticated user'}, status=401)

    logout(request)
    return JsonResponse({'message': 'Successfully logged out'})


def csrf_token_view(request):
    return JsonResponse({'token': get_token(request)})
