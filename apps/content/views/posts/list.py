import json
import re

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from apps.content.models import Category, Post, Tag
from apps.content.serializers import PostSerializer
from apps.utils.decorators import admin_or_author_required, login_required
from apps.utils.text import normalize_text


class PostListView(View):
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self, *args, **kwargs):
        queryset = Post.objects.all()
        # Filtering
        category = self.request.GET.get('category')
        tags = self.request.GET.get('tags')
        search = self.request.GET.get('search')

        if category:
            queryset = queryset.filter(category__slug=category)

        if tags:
            tag_slugs = tags.split(',')
            queryset = queryset.filter(tags__slug__in=tag_slugs).distinct()

        if search:
            search_normalized = normalize_text(search)
            keywords = re.findall(r'\w+', search_normalized)
            query = Q()
            for keyword in keywords:
                query |= Q(title__icontains=keyword)
            queryset = queryset.filter(query)
        return queryset

    def get(self, request, *args, **kwargs):
        response_data = {
            'data': list(
                PostSerializer.serialize_post(post) for post in self.get_queryset()
            )
        }
        return JsonResponse(response_data, status=200)

    @method_decorator([login_required, admin_or_author_required])
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            allowed_fields = {'title', 'content', 'category', 'tags'}
            invalid_fields = set(data.keys()) - allowed_fields
            if invalid_fields:
                return JsonResponse(
                    {'error': f'Invalid fields: {", ".join(invalid_fields)}'},
                    status=400,
                )
            category_slug = data.get('category')
            if not category_slug:
                return JsonResponse({'error': 'Category is required'}, status=400)
            category = Category.objects.filter(slug=category_slug).first()

            if not category:
                return JsonResponse({'error': 'Category not found'}, status=404)

            post = Post(
                title=data.get('title'),
                content=data.get('content'),
                category=category,
                author=self.request.user,
                status=Post.Status.DRAFT,
            )

            tag_slugs = set(data.get('tags', []))
            tags = {tag.slug: tag for tag in Tag.objects.filter(slug__in=tag_slugs)}
            invalid_tags = tag_slugs - tags.keys()

            if invalid_tags:
                return JsonResponse(
                    {'error': f'Tags not found: {", ".join(invalid_tags)}'},
                    status=404,
                )

            post.save()
            if tags:
                post.tags.set(tags.values())
            return JsonResponse(
                {'data': PostSerializer.serialize_post(post)}, status=201
            )
        except json.JSONDecodeError as e:
            return JsonResponse({'error': e.msg}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
