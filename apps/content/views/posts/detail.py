import json

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from apps.content.models import Category, Post
from apps.content.serializers import PostSerializer
from apps.utils.decorators import admin_or_author_required, login_required
from apps.utils.jsonapi_responses import JsonApiResponseBuilder as jarb
from apps.utils.validators import get_valid_tags_or_404, validate_invalid_fields


class PostDetailView(View):
    http_method_names = ['get', 'patch', 'put', 'delete', 'head', 'options']

    def get(self, request, *args, **kwargs):
        try:
            post = get_object_or_404(Post, slug=self.kwargs.get('slug'))
            data = PostSerializer.serialize_post(post)

            if data['relationships']:
                data['included'] = PostSerializer.build_included_data(post)

            if post.is_public():
                return jarb.ok(data)

            if request.user.is_authenticated and (
                request.user.role == 'admin' or request.user.id == post.author.id
            ):
                return jarb.ok(data)

            else:
                return jarb.error(
                    403, 'Forbidden', 'You do not have permission to view this post'
                )
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_or_author_required])
    def patch(self, request, *args, **kwargs):
        try:
            post = get_object_or_404(Post, slug=self.kwargs.get('slug'))
            if not (request.user.role == 'admin' or request.user.id == post.author.id):
                return jarb.error(
                    403, 'Forbidden', 'You do not have permission to edit this post'
                )
            data = json.loads(request.body)

            allowed_fields = {'title', 'content', 'category', 'tags', 'status'}
            validate_invalid_fields(data, allowed_fields)

            if 'category' in data:
                category = get_object_or_404(Category, slug=data['category'])
                post.category = category

            if 'tags' in data:
                post.tags.set(get_valid_tags_or_404(data['tags']))

            for field in set(data.keys()) - {'category', 'tags'}:
                setattr(post, field, data[field])

            post.save()
            return jarb.ok(PostSerializer.serialize_post(post))
        except json.JSONDecodeError as e:
            return jarb.error(400, 'Bad Request', f'Invalid JSON: {str(e)}')
        except ValidationError as e:
            return jarb.validation_errors_from_dict(e.message_dict)
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_or_author_required])
    def delete(self, request, *args, **kwargs):
        try:
            post = get_object_or_404(Post, slug=self.kwargs.get('slug'))

            if not (request.user.role == 'admin' or request.user.id == post.author.id):
                return jarb.error(
                    403, 'Forbidden', 'You do not have permission to delete this post'
                )

            post.delete()
            return jarb.no_content()
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))
