from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryListView,
    PostDetailView,
    PostListView,
    PostMediaFileDetailView,
    PostMediaFileListView,
    TagDetailView,
    TagListView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path(
        'categories/<str:slug>/', CategoryDetailView.as_view(), name='category-detail'
    ),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/<str:slug>/', TagDetailView.as_view(), name='tag-detail'),
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<str:slug>/', PostDetailView.as_view(), name='post-detail'),
    path(
        'posts/<str:slug>/media/',
        PostMediaFileListView.as_view(),
        name='post-media-list',
    ),
    path(
        'posts/<str:slug>/media/<int:id>/',
        PostMediaFileDetailView.as_view(),
        name='post-media-detail',
    ),
]
