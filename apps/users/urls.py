from django.urls import path

from .views import (
    AuthorProfileDetailView,
    SocialAccountDetailView,
    SocialAccountListView,
    UserDetailView,
    UserListView,
    csrf_token_view,
    login_view,
    logout_view,
)

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path(
        'users/<int:user_id>/profile/',
        AuthorProfileDetailView.as_view(),
        name='author-profile-detail',
    ),
    path(
        'users/<int:user_id>/social-accounts/',
        SocialAccountListView.as_view(),
        name='social-account-list',
    ),
    path(
        'users/<int:user_id>/social-accounts/<int:social_id>/',
        SocialAccountDetailView.as_view(),
        name='social-account-detail',
    ),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/csrf-token/', csrf_token_view, name='csrf-token'),
]
