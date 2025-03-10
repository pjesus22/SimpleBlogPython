from django.http import JsonResponse
from django.views.generic import DetailView, ListView

from ..models import Post
from ..serializers.post import PostSerializer


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(
            {
                'data': [
                    PostSerializer.serialize_post(post) for post in context['posts']
                ]
            },
            safe=False,
        )


class PostDetailView(DetailView):
    model = Post
    slug_field = 'slug'
    context_object_name = 'post'

    def render_to_response(self, context, **response_kwargs):
        post = context['post']
        response_data = {
            'data': PostSerializer.serialize_post(post),
            'included': PostSerializer.build_included_data(post),
        }
        return JsonResponse(response_data, safe=False)
