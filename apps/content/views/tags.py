import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from apps.utils.permission_decorators import admin_required, login_required

from ..models import Tag
from ..serializers import TagSerializer


class TagListView(View):
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return Tag.objects.all()

    def get(self, request, *args, **kwargs):
        response_data = {
            'data': [TagSerializer.serialize_tag(tag) for tag in self.get_queryset()]
        }
        return JsonResponse(response_data)

    @method_decorator([login_required, admin_required])
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            tag = Tag(name=data.get('name'))

            tag.save()
            return JsonResponse(TagSerializer.serialize_tag(tag), status=201)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': e.msg}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)


class TagDetailView(View):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_object(self):
        return Tag.objects.filter(slug=self.kwargs.get('slug')).first()

    def get(self, request, *args, **kwargs):
        tag = self.get_object()

        if not tag:
            return JsonResponse({'error': 'Tag not found'}, status=404)

        response_data = {'data': TagSerializer.serialize_tag(tag)}
        included = TagSerializer.build_included_data(tag)

        if included:
            response_data['included'] = included

        return JsonResponse(response_data)

    @method_decorator([login_required, admin_required])
    def patch(self, request, *args, **kwargs):
        try:
            tag = self.get_object()

            if not tag:
                return JsonResponse({'error': 'Tag not found'}, status=404)

            data = json.loads(request.body)
            allowed_fields = {'name'}
            invalid_fields = set(data) - allowed_fields

            if invalid_fields:
                return JsonResponse(
                    {'error': f'Invalid fields: {", ".join(invalid_fields)}'},
                    status=400,
                )

            tag.name = data.get('name')

            tag.save()
            return JsonResponse(TagSerializer.serialize_tag(tag), status=200)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': e.msg}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)

    @method_decorator([login_required, admin_required])
    def delete(self, request, *args, **kwargs):
        tag = self.get_queryset()

        if not tag:
            return JsonResponse({'error': 'Tag not found'}, status=404)

        tag.delete()
        return HttpResponse(status=204)
