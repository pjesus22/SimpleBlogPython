from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from apps.utils.jsonapi_responses import JsonApiResponseBuilder as jarb

from ..utils.decorators import admin_required, login_required
from .models import MediaFile
from .serializers import MediaFileSerializer


class MediaFileListView(View):
    http_method_names = ['get', 'head', 'options']

    @method_decorator([login_required, admin_required])
    def get(self, request, *args, **kwargs):
        try:
            queryset = MediaFile.objects.all()
            response_data = MediaFileSerializer.serialize_media_files(queryset)
            return jarb.ok(response_data)
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))


class MediaFileDetailView(View):
    http_method_names = ['get', 'head', 'options']

    @method_decorator([login_required, admin_required])
    def get(self, request, *args, **kwargs):
        try:
            media_file = get_object_or_404(MediaFile, id=kwargs.get('id'))
            response_data = MediaFileSerializer.serialize_media_file(media_file)
            return jarb.ok(response_data)
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))
