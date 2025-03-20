from django.urls import path

from .views import (
    UserDetailView,
    UserListView,
    csrf_token_view,
    login_view,
    logout_view,
)

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/csrf-token/', csrf_token_view, name='csrf-token'),
]
