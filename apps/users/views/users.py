import json

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from apps.utils.decorators import (
    admin_or_author_required,
    admin_required,
    login_required,
)
from apps.utils.jsonapi_responses import JsonApiResponseBuilder as jarb
from apps.utils.validators import (
    validate_invalid_fields,
    validate_required_fields,
)

from ..models import Author, User
from ..serializers import UserSerializer


class UserListView(View):
    http_method_names = ['get', 'post', 'head', 'options']

    @method_decorator([login_required, admin_required])
    def get(self, request, *args, **kwargs):
        try:
            data = [UserSerializer.serialize_user(user) for user in User.objects.all()]
            return jarb.ok(data)
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

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
            }
            required_fields = {'username', 'email', 'password', 'role'}

            validate_invalid_fields(data, allowed_fields | required_fields)
            validate_required_fields(data, required_fields)

            filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

            user = Author(**{k: v for k, v in filtered_data.items() if k != 'password'})
            user.set_password(filtered_data['password'])

            user.save()
            return jarb.created(UserSerializer.serialize_user(user))
        except (json.JSONDecodeError, ValidationError) as e:
            return jarb.error(400, 'Bad Request', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))


class UserDetailView(View):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    @method_decorator([login_required, admin_or_author_required])
    def get(self, request, *args, **kwargs):
        try:
            user = get_object_or_404(User, pk=self.kwargs.get('pk'))

            if not (request.user.role == 'admin' or request.user.id == user.id):
                return jarb.error(
                    403, 'Forbidden', 'You do not have permission to view this user'
                )

            data = UserSerializer.serialize_user(user)

            if data['relationships']:
                data['included'] = UserSerializer.build_included_data(user)

            return jarb.ok(data)
        except Http404:
            return jarb.error(404, 'Not Found', 'User not found')
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_or_author_required])
    def patch(self, request, *args, **kwargs):
        try:
            user = get_object_or_404(User, pk=self.kwargs.get('pk'))

            if not (request.user.role == 'admin' or request.user.id == user.id):
                return jarb.error(
                    403, 'Forbidden', 'You do not have permission to edit this user'
                )

            data = json.loads(request.body)
            allowed_fields = {
                'username',
                'email',
                'password',
                'first_name',
                'last_name',
            }

            validate_invalid_fields(data, allowed_fields)

            for field, value in data.items():
                if value in ['', None]:
                    raise ValidationError(f'The {field} field cannot be empty or null.')
                if field == 'password':
                    user.set_password(value)
                else:
                    setattr(user, field, value)

            user.save()
            return jarb.ok(UserSerializer.serialize_user(user))
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            return jarb.error(400, 'Bad Request', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_or_author_required])
    def delete(self, request, *args, **kwargs):
        try:
            user = get_object_or_404(User, pk=self.kwargs.get('pk'))

            if not (request.user.role == 'admin' or request.user.id == user.id):
                return jarb.error(
                    403, 'Forbidden', 'You do not have permission to delete this user'
                )

            user.delete()
            return jarb.no_content()
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))
