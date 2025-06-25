from django.urls import path

from .views import MediaFileDetailView, MediaFileListView

urlpatterns = [
    path('media/', MediaFileListView.as_view(), name='media-list'),
    path('media/<int:id>/', MediaFileDetailView.as_view(), name='media-detail'),
]
