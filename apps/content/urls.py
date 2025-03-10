from django.urls import path

from .views.categories import CategoryDetailView, CategoryListView
from .views.posts import PostDetailView, PostListView
from .views.tags import TagDetailView, TagListView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path(
        'categories/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'
    ),
    path('tags/', TagListView.as_view(), name='tag_list'),
    path('tags/<str:slug>/', TagDetailView.as_view(), name='tag_detail'),
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/<str:slug>/', PostDetailView.as_view(), name='post_detail'),
]
