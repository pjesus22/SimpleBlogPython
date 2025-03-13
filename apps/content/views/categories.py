from django.http import Http404, JsonResponse
from django.views.generic import DetailView, ListView

from ..models import Category
from ..serializers import CategorySerializer


class CategoryListView(ListView):
    model = Category
    context_object_name = 'categories'

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        categories = context['categories']
        response_data = {
            'data': [
                CategorySerializer.serialize_category(category)
                for category in categories
            ]
        }
        return JsonResponse(response_data, safe=False)


class CategoryDetailView(DetailView):
    model = Category
    slug_field = 'slug'
    context_object_name = 'category'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Category.DoesNotExist:
            raise Http404('Category not found')

        context = self.get_context_data()
        category = context['category']
        response_data = {'data': CategorySerializer.serialize_category(category)}
        included = CategorySerializer.build_included_data(category)

        if included:
            response_data['included'] = included

        return JsonResponse(response_data)
