from django.http import JsonResponse
from django.views.generic import DetailView, ListView

from ..models import Tag
from ..serializers.tags import TagSerializer


class TagListView(ListView):
    model = Tag
    context_object_name = 'tags'

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(
            {'data': [TagSerializer.serialize_tag(tag) for tag in context['tags']]},
            safe=False,
        )


class TagDetailView(DetailView):
    model = Tag
    slug_field = 'slug'
    context_object_name = 'tag'

    def render_to_response(self, context, **response_kwargs):
        tag = context['tag']
        included = TagSerializer.build_included_data(tag)
        response_data = {
            'data': TagSerializer.serialize_tag(tag),
        }
        if included:
            response_data['included'] = included
        return JsonResponse(response_data)
