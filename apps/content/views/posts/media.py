import json

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from apps.content.models import Post
from apps.media_files.models import MediaFile
from apps.media_files.serializers import MediaFileSerializer
from apps.utils.decorators import admin_or_author_required, login_required
from apps.utils.jsonapi_responses import JsonApiResponseBuilder as jarb


class PostMediaFileListView(View):
    http_method_names = ['get', 'post', 'head', 'options']

    def get(self, request, *args, **kwargs):
        try:
            post = get_object_or_404(Post, slug=self.kwargs.get('slug'))

            if post.is_public() and not request.user.is_authenticated:
                serialized_data = MediaFileSerializer.serialize_media_files(
                    post.media_files.all(), public=True
                )
                return jarb.ok(serialized_data)

            if request.user.is_authenticated and (
                (request.user.role == 'author' and request.user.id == post.author.id)
                or request.user.role == 'admin'
            ):
                serialized_data = MediaFileSerializer.serialize_media_files(
                    post.media_files.all(), public=False
                )
                return jarb.ok(serialized_data)
            return jarb.error(
                403, 'Forbidden', 'You do not have permission to view these media files'
            )
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_or_author_required])
    def post(self, request, *args, **kwargs):
        try:
            post = get_object_or_404(Post, slug=self.kwargs.get('slug'))
            if not (request.user.role == 'admin' or request.user.id == post.author.id):
                return jarb.error(
                    403, 'Forbidden', 'You do not have permission to add media files'
                )

            files = request.FILES.getlist('files')
            if not files:
                return jarb.error(400, 'Bad Request', 'No files provided')

            media_files = []
            for file in files:
                media_file = MediaFile(post=post, file=file)
                media_file.save()
                media_files.append(media_file)

            data = MediaFileSerializer.serialize_media_files(media_files, public=False)
            return jarb.created(data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            return jarb.error(400, 'Bad Request', str(e))
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))


class PostMediaFileDetailView(View):
    http_method_names = ['get', 'delete', 'head', 'options']

    def get(self, request, *args, **kwargs):
        try:
            media_file = get_object_or_404(
                MediaFile,
                id=self.kwargs.get('id'),
                post__slug=self.kwargs.get('slug'),
            )

            if media_file.post.is_public() and not request.user.is_authenticated:
                data = MediaFileSerializer.serialize_media_file(media_file, public=True)
                return jarb.ok(data)

            if request.user.is_authenticated and (
                (
                    request.user.role == 'author'
                    and request.user.id == media_file.post.author.id
                )
                or request.user.role == 'admin'
            ):
                data = MediaFileSerializer.serialize_media_file(
                    media_file, public=False
                )
                return jarb.ok(data)
            else:
                return jarb.error(
                    403,
                    'Forbidden',
                    'You do not have permission to view this media file',
                )
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_or_author_required])
    def delete(self, request, *args, **kwargs):
        try:
            media_file = media_file = get_object_or_404(
                MediaFile, id=self.kwargs.get('id'), post__slug=self.kwargs.get('slug')
            )

            if not (
                request.user.role == 'admin'
                or request.user.id == media_file.post.author.id
            ):
                return jarb.error(
                    403,
                    'Forbidden',
                    'You do not have permission to delete this media file',
                )

            media_file.file.delete(save=False)
            media_file.delete()
            return jarb.no_content()
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))
