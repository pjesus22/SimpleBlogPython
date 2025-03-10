from django.http import JsonResponse
from django.views.generic import DetailView, ListView

from .models import User
from .serializers import UserSerializer


class UserListView(ListView):
    model = User
    context_object_name = 'users'

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(
            {
                'data': [
                    UserSerializer.serialize_user(user) for user in context['users']
                ]
            },
            safe=False,
        )


class UserDetailView(DetailView):
    model = User
    context_object_name = 'user'

    def render_to_response(self, context, **response_kwargs):
        user = context['user']
        response_data = {
            'data': UserSerializer.serialize_user(user),
            'included': UserSerializer.build_included_data(user),
        }
        return JsonResponse(response_data, safe=False)
