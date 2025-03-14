from django.http import Http404, JsonResponse
from django.views.generic import DetailView, ListView

from ..models import Tag
from ..serializers import TagSerializer


class TagListView(ListView):
    model = Tag
    context_object_name = 'tags'

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        tags = context['tags']
        response_data = {'data': [TagSerializer.serialize_tag(tag) for tag in tags]}
        return JsonResponse(response_data, safe=False)


class TagDetailView(DetailView):
    model = Tag
    slug_field = 'slug'
    context_object_name = 'tag'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            return JsonResponse(
                {'error': f'Tag {kwargs["slug"]} not found'}, status=404
            )

        context = self.get_context_data()
        tag = context['tag']
        response_data = {'data': TagSerializer.serialize_tag(tag)}
        included = TagSerializer.build_included_data(tag)

        if included:
            response_data['included'] = included

        return JsonResponse(response_data)
