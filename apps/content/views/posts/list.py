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
from apps.utils.query_filters import filter_posts_by_params, filter_posts_by_user_role
from apps.utils.validators import (
    get_valid_tags_or_404,
    validate_invalid_fields,
    validate_required_fields,
)


class PostListView(View):
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        queryset = Post.objects.all()
        queryset = filter_posts_by_user_role(queryset, user)
        queryset = filter_posts_by_params(queryset, self.request.GET)
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            data = [PostSerializer.serialize_post(post) for post in queryset]
            return jarb.ok(data)

        except ValidationError as e:
            return jarb.error(400, 'Bad Request', str(e))
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_or_author_required])
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            allowed_fields = {
                'title',
                'content',
                'category',
                'tags',
            }
            required_fields = [
                'title',
                'content',
                'category',
            ]

            validate_invalid_fields(data, allowed_fields)
            validate_required_fields(data, required_fields)

            category = get_object_or_404(Category, slug=data.get('category'))

            tag_slugs = data.get('tags') or []
            tags = get_valid_tags_or_404(tag_slugs)

            post = Post(
                title=data.get('title'),
                content=data.get('content'),
                category=category,
                author=self.request.user,
                status=Post.Status.DRAFT,
            )

            post.save()
            post.tags.set(tags.values())

            return jarb.created(PostSerializer.serialize_post(post))
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            return jarb.error(400, 'Bad Request', str(e))
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))
