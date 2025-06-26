from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from apps.utils.jsonapi_responses import JsonApiResponseBuilder as jarb

from ..utils.decorators import admin_required, login_required
from .models import MediaFile
from .serializers import MediaFileSerializer


class MediaFileListView(View):
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        return MediaFile.objects.all()

    @method_decorator([login_required, admin_required])
    def get(self, request, *args, **kwargs):
        response_data = {
            'data': MediaFileSerializer.serialize_media_files(self.get_queryset())
        }
        return JsonResponse(response_data)


class MediaFileDetailView(View):
    http_method_names = ['get', 'head', 'options']

    @method_decorator([login_required, admin_required])
    def get(self, request, *args, **kwargs):
        try:
            media_file = get_object_or_404(MediaFile, id=kwargs.get('id'))
            response_data = MediaFileSerializer.serialize_media_file(media_file)
            return jarb.ok(response_data)
        except Http404:
            return jarb.error(404, 'Not Found', 'Media file not found')
