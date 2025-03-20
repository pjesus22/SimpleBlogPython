import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from ...utils.permission_decorators import admin_or_author_required, login_required
from ..models import Category, Post, Tag
from ..serializers import PostSerializer


class PostDetailView(View):
    http_method_names = ['get', 'patch', 'put', 'delete', 'head', 'options']

    def get_object(self):
        return Post.objects.filter(slug=self.kwargs.get('slug')).first()

    def get(self, request, *args, **kwargs):
        post = self.get_object()

        if not post:
            return JsonResponse({'error': 'Post not found'}, status=404)

        response_data = {'data': PostSerializer.serialize_post(post)}
        included = PostSerializer.build_included_data(post)

        if included:
            response_data['included'] = included

        return JsonResponse(response_data)

    @method_decorator([login_required, admin_or_author_required])
    def patch(self, request, *args, **kwargs):
        try:
            post = self.get_object()

            if not post:
                return JsonResponse({'error': 'Post not found'}, status=404)

            if not (request.user.role == 'admin' or request.user.id == post.author.id):
                return JsonResponse({'error': 'Permission denied'}, status=403)

            data = json.loads(request.body)
            allowed_fields = {'title', 'content', 'category', 'tags', 'status'}
            invalid_fields = set(data) - allowed_fields

            if invalid_fields:
                return JsonResponse(
                    {'error': f'Invalid fields: {", ".join(invalid_fields)}'},
                    status=400,
                )

            if 'category' in data:
                category = Category.objects.filter(slug=data['category']).first()
                if not category:
                    return JsonResponse({'error': 'Category not found'}, status=404)
                post.category = category

            if 'tags' in data:
                tag_slugs = set(data['tags'])
                tags = {tag.slug: tag for tag in Tag.objects.filter(slug__in=tag_slugs)}
                invalid_tags = tag_slugs - tags.keys()

                if invalid_tags:
                    return JsonResponse(
                        {'error': f'Invalid tags: {", ".join(invalid_tags)}'},
                        status=400,
                    )

                post.tags.set(tags.values())

            for field in allowed_fields - {'category', 'tags'}:
                if field in data:
                    setattr(post, field, data[field])

            post.save()
            return JsonResponse(PostSerializer.serialize_post(post), status=200)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': e.msg}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    @method_decorator([login_required, admin_or_author_required])
    def delete(self, request, *args, **kwargs):
        try:
            post = self.get_object()

            if not post:
                return JsonResponse({'error': 'Post not found'}, status=404)

            if not (request.user.role == 'admin' or request.user.id == post.author.id):
                return JsonResponse({'error': 'Permission denied'}, status=403)

            post.delete()
            return HttpResponse(status=204)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
