from django.urls import path

from .views import MediaFileListView

urlpatterns = [path('media/', MediaFileListView.as_view(), name='media-list')]
