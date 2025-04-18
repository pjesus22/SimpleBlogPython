import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from apps.utils.decorators import (
    admin_or_author_required,
    admin_required,
    login_required,
)

from ..models import User
from ..serializers import UserSerializer


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
            invalid_fields = set(data) - allowed_fields
            if invalid_fields:
                return JsonResponse(
                    {'error': f'Invalid fields: {", ".join(invalid_fields)}'},
                    status=400,
                )

            filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

            user = User(**{k: v for k, v in filtered_data.items() if k != 'password'})
            user.set_password(filtered_data['password'])

            user.full_clean()
            user.save()
            return JsonResponse(
                {'data': UserSerializer.serialize_user(user)}, status=201
            )
        except json.JSONDecodeError as e:
            return JsonResponse({'error': e.msg}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class UserDetailView(View):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_object(self):
        return User.objects.filter(pk=self.kwargs.get('pk')).first()

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
            return JsonResponse(
                {'data': UserSerializer.serialize_user(user)}, status=200
            )
        except json.JSONDecodeError as e:
            return JsonResponse({'error': e.msg}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    @method_decorator([login_required, admin_or_author_required])
    def delete(self, request, *args, **kwargs):
        try:
            user = self.get_object()

            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)

            if not (request.user.role == 'admin' or request.user.id == user.id):
                return JsonResponse({'error': 'Permission denied'}, status=403)

            user.delete()
            return HttpResponse(status=204)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
