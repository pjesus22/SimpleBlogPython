from django.http import JsonResponse
from django.views.generic import DetailView, ListView

from ..models import Category
from ..serializers.categories import CategorySerializer


class CategoryListView(ListView):
    model = Category
    context_object_name = 'categories'

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(
            {
                'data': [
                    CategorySerializer.serialize_category(category)
                    for category in context['categories']
                ]
            },
            safe=False,
        )


class CategoryDetailView(DetailView):
    model = Category
    slug_field = 'slug'
    context_object_name = 'category'

    def render_to_response(self, context, **response_kwargs):
        category = context['category']
        included = CategorySerializer.build_included_data(category)
        response_data = {
            'data': CategorySerializer.serialize_category(category),
        }
        if included:
            response_data['included'] = included
            return JsonResponse(response_data)
        return JsonResponse(response_data)
