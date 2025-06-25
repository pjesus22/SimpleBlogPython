import json

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from apps.utils.decorators import admin_required, login_required
from apps.utils.jsonapi_responses import JsonApiResponseBuilder as jarb
from apps.utils.validators import validate_invalid_fields, validate_required_fields

from ..models import Category
from ..serializers import CategorySerializer


class CategoryListView(View):
    http_method_names = ['get', 'post', 'head', 'options']

    def get(self, request, *args, **kwargs):
        try:
            queryset = Category.objects.all()
            data = [
                CategorySerializer.serialize_category(category) for category in queryset
            ]
            return jarb.ok(data)
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_required])
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            validate_invalid_fields(data, {'name', 'description'})
            validate_required_fields(data, ['name'])

            category = Category(
                name=data.get('name'),
                description=data.get('description'),
            )
            category.save()

            return jarb.created(CategorySerializer.serialize_category(category))
        except (ValidationError, ValueError, json.JSONDecodeError) as e:
            return jarb.error(400, 'Bad Request', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))


class CategoryDetailView(View):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get(self, request, *args, **kwargs):
        try:
            category = get_object_or_404(Category, slug=self.kwargs.get('slug'))
            data = CategorySerializer.serialize_category(category)

            if data['relationships']:
                data['included'] = CategorySerializer.build_included_data(category)

            return jarb.ok(data)
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_required])
    def patch(self, request, *args, **kwargs):
        try:
            category = get_object_or_404(Category, slug=self.kwargs.get('slug'))
            data = json.loads(request.body)

            allowed_fields = {'name', 'description'}
            validate_invalid_fields(data, allowed_fields)

            for field, value in data.items():
                if value in ['', None]:
                    raise ValidationError(f'The {field} field cannot be empty or null.')
                setattr(category, field, value)

            category.save()
            return jarb.ok(CategorySerializer.serialize_category(category))
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            return jarb.error(400, 'Bad Request', str(e))
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_required])
    def delete(self, request, *args, **kwargs):
        try:
            category = get_object_or_404(Category, slug=self.kwargs.get('slug'))
            category.delete()
            return jarb.no_content()
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))
