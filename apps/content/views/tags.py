import json

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from apps.utils.decorators import admin_required, login_required
from apps.utils.jsonapi_responses import JsonApiResponseBuilder as jarb
from apps.utils.validators import validate_invalid_fields, validate_required_fields

from ..models import Tag
from ..serializers import TagSerializer


class TagListView(View):
    http_method_names = ['get', 'post', 'head', 'options']

    def get(self, request, *args, **kwargs):
        try:
            queryset = Tag.objects.all()
            data = [TagSerializer.serialize_tag(tag) for tag in queryset]
            return jarb.ok(data)
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_required])
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            validate_invalid_fields(data, {'name'})
            validate_required_fields(data, ['name'])

            tag = Tag(name=data.get('name'))
            tag.save()

            return jarb.created(TagSerializer.serialize_tag(tag))
        except json.JSONDecodeError as e:
            return jarb.error(400, 'Bad Request', f'Invalid JSON: {str(e)}')
        except ValidationError as e:
            return jarb.validation_errors_from_dict(e.message_dict)
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))


class TagDetailView(View):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get(self, request, *args, **kwargs):
        try:
            tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
            data = TagSerializer.serialize_tag(tag)

            if data['relationships']:
                data['included'] = TagSerializer.build_included_data(tag)

            return jarb.ok(data)
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_required])
    def patch(self, request, *args, **kwargs):
        try:
            tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
            data = json.loads(request.body)

            validate_invalid_fields(data, {'name'})

            if data.get('name') in [None, '']:
                raise ValidationError({'name': 'This field cannot be empty or null.'})

            tag.name = data.get('name')
            tag.save()
            return jarb.ok(TagSerializer.serialize_tag(tag))
        except json.JSONDecodeError as e:
            return jarb.error(400, 'Bad Request', f'Invalid JSON: {str(e)}')
        except ValidationError as e:
            return jarb.validation_errors_from_dict(e.message_dict)
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_required])
    def delete(self, request, *args, **kwargs):
        try:
            tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
            tag.delete()
            return jarb.no_content()
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))
