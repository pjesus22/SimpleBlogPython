import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from apps.utils.permission_decorators import admin_required, login_required

from ..models import Category
from ..serializers import CategorySerializer


class CategoryListView(View):
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return Category.objects.all()

    def get(self, request, *args, **kwargs):
        response_data = {
            'data': [
                CategorySerializer.serialize_category(category)
                for category in self.get_queryset()
            ]
        }
        return JsonResponse(response_data)

    @method_decorator([login_required, admin_required])
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            allowed_fields = {'name', 'description'}

            if not set(data.keys()) <= allowed_fields:
                return JsonResponse(
                    {'error': f'Invalid fields: {", ".join(data.keys())}'},
                    status=400,
                )

            category = Category(
                name=data.get('name'), description=data.get('description')
            )

            category.save()
            return JsonResponse(
                CategorySerializer.serialize_category(category), status=201
            )
        except json.JSONDecodeError as e:
            return JsonResponse({'error': e.msg}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CategoryDetailView(View):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_object(self):
        return Category.objects.filter(slug=self.kwargs.get('slug')).first()

    def get(self, request, *args, **kwargs):
        category = self.get_object()

        if not category:
            return JsonResponse({'error': 'Category not found'}, status=404)

        response_data = {'data': CategorySerializer.serialize_category(category)}
        included = CategorySerializer.build_included_data(category)

        if included:
            response_data['included'] = included

        return JsonResponse(response_data)

    @method_decorator([login_required, admin_required])
    def patch(self, request, *args, **kwargs):
        try:
            category = self.get_object()

            if not category:
                return JsonResponse({'error': 'Category not found'}, status=404)

            data = json.loads(request.body)
            allowed_fields = {'description'}
            invalid_fields = set(data) - allowed_fields

            if invalid_fields:
                return JsonResponse(
                    {'error': f'Invalid fields: {", ".join(invalid_fields)}'},
                    status=400,
                )

            for field in allowed_fields & data.keys():
                setattr(category, field, data[field])

            category.save()
            return JsonResponse(
                CategorySerializer.serialize_category(category), status=200
            )
        except json.JSONDecodeError as e:
            return JsonResponse({'error': e.msg}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    @method_decorator([login_required, admin_required])
    def delete(self, request, *args, **kwargs):
        try:
            category = self.get_queryset()

            if not category:
                return JsonResponse({'error': 'Category not found'}, status=404)

            category.delete()
            return HttpResponse(status=204)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
