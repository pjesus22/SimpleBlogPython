from django.http import Http404, JsonResponse
from django.views.generic import DetailView, ListView

from ..models import Post
from ..serializers import PostSerializer


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        posts = context['posts']
        response_data = {
            'data': [PostSerializer.serialize_post(post) for post in posts]
        }
        return JsonResponse(response_data, safe=False)


class PostDetailView(DetailView):
    model = Post
    slug_field = 'slug'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Post.DoesNotExist:
            raise Http404('Post not found')

        context = self.get_context_data()
        post = context['post']
        response_data = {'data': PostSerializer.serialize_post(post)}
        included = PostSerializer.build_included_data(post)

        if included:
            response_data['included'] = included

        return JsonResponse(response_data)
