from django.urls import path
from .views import PostsList, PostDetail

urlpatterns = [
    path('', PostsList.as_view(), name='news_list'),
    path('<int:pk>/', PostDetail.as_view(), name='news_detail'),
]