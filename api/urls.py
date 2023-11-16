from django.urls import path

from main.views import bbs, BbDetailView, comments, CommentListCreate

app_name = 'api'

urlpatterns = [
    # path('bbs/<int:pk>/comments', comments, name='bbs-detail-comments'),
    path('bbs/<int:pk>/comments', CommentListCreate.as_view(), name='bbs-detail-comments'),
    path('bbs/<int:pk>', BbDetailView.as_view(), name='bbs-detail'),
    path('bbs/', bbs, name='bbs-list'),
]
