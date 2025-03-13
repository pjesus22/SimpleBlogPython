from django.http import Http404, JsonResponse
from django.views.generic import DetailView, ListView

from .models import User
from .serializers import UserSerializer


class UserListView(ListView):
    model = User
    context_object_name = 'users'

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        users = context['users']
        response_data = {
            'data': [UserSerializer.serialize_user(user) for user in users]
        }
        return JsonResponse(response_data, safe=False)


class UserDetailView(DetailView):
    model = User
    context_object_name = 'user'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except User.DoesNotExist:
            raise Http404('User not found')

        context = self.get_context_data()
        user = context['user']
        response_data = {'data': UserSerializer.serialize_user(user)}
        included = UserSerializer.build_included_data(user)

        if included:
            response_data['included'] = included

        return JsonResponse(response_data)
