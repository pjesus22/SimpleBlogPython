from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

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
