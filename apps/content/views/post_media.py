from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from ...media_files.models import MediaFile
from ...media_files.serializers import MediaFileSerializer
from ...utils.permission_decorators import admin_or_author_required, login_required
from ..models import Post


class PostMediaFileListView(View):
    http_method_names = ['get', 'post', 'head', 'options']

    def get_object(self):
        return Post.objects.filter(slug=self.kwargs.get('slug')).first()

    def get(self, request, *args, **kwargs):
        post = self.get_object()

        if not post:
            return JsonResponse({'error': 'Post not found'}, status=404)

        serialized_data = MediaFileSerializer.serialize_media_files(
            post.media_files.all()
        )
        return JsonResponse({'data': serialized_data})

    @method_decorator([login_required, admin_or_author_required])
    def post(self, request, *args, **kwargs):
        try:
            post = self.get_object()

            if not post:
                return JsonResponse({'error': 'Post not found'}, status=404)

            if not (request.user.role == 'admin' or request.user.id == post.author.id):
                return JsonResponse({'error': 'Permission denied'}, status=403)

            files = request.FILES.getlist('files')
            media_files = []

            for file in files:
                media_file = MediaFile(post=post, file=file)
                media_file.save()
                media_files.append(media_file)

            serialized_data = MediaFileSerializer.serialize_media_files(media_files)
            return JsonResponse({'data': serialized_data}, status=201)
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class PostMediaFileDetailView(View):
    http_method_names = ['get', 'delete', 'head', 'options']

    def get_object(self):
        return MediaFile.objects.filter(id=self.kwargs.get('id')).first()

    def get(self, request, *args, **kwargs):
        media_file = self.get_object()

        if not media_file:
            return JsonResponse({'error': 'Media file not found'}, status=404)

        serialized_data = MediaFileSerializer.serialize_media_file(media_file)
        return JsonResponse({'data': serialized_data})

    @method_decorator([login_required, admin_or_author_required])
    def delete(self, request, *args, **kwargs):
        try:
            media_file = self.get_object()

            if not media_file:
                return JsonResponse({'error': 'Media file not found'}, status=404)

            if not (
                request.user.role == 'admin'
                or request.user.id == media_file.post.author.id
            ):
                return JsonResponse({'error': 'Permission denied'}, status=403)

            media_file.file.delete(save=False)
            media_file.delete()
            return HttpResponse(status=204)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
