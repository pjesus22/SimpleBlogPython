import re

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404

from apps.content.models import Category, Post, Tag
from apps.utils.text import normalize_text


def filter_posts_by_user_role(queryset, user):
    if not user.is_authenticated:
        return queryset.filter(status=Post.Status.PUBLISHED)
    elif user.role == 'author':
        return (
            queryset.filter(Q(author=user) | Q(status=Post.Status.PUBLISHED))
            .distinct()
            .order_by('-id')
        )
    elif user.role == 'admin':
        return queryset
    else:
        return queryset.filter(status=Post.Status.PUBLISHED)


def filter_posts_by_params(queryset, params):
    category = params.get('category')
    tags = params.get('tags')
    search = params.get('search')

    if category:
        if not re.match(r'^[-\w]+$', category):
            raise ValidationError({'category': 'Invalid slug format.'})
        if not Category.objects.filter(slug=category).exists():
            raise Http404('No Category matches the given query.')
        queryset = queryset.filter(category__slug=category)

    if tags:
        tags_slugs = [slug for slug in tags.split(',') if slug]
        for slug in tags_slugs:
            if not re.match(r'^[-\w]+$', slug):
                raise ValidationError({'tags': 'Invalid slug format.'})

        existing_slugs = Tag.objects.filter(slug__in=tags_slugs).values_list(
            'slug', flat=True
        )
        missing = set(tags_slugs) - set(existing_slugs)

        if missing:
            raise Http404(f'The following tags were not found: {", ".join(missing)}.')

        queryset = queryset.filter(tags__slug__in=tags_slugs).distinct()

    if search:
        if not re.match(r'^[\w\s\-]*$', search):
            raise ValidationError({'search': 'Invalid search query format.'})

        search_normalized = normalize_text(search)
        keywords = re.findall(r'\w+', search_normalized)
        query = Q()
        for keyword in keywords:
            query |= Q(title__icontains=keyword)
        queryset = queryset.filter(query)
        if not queryset.exists():
            raise Http404('No Post matches the given query.')

    return queryset
