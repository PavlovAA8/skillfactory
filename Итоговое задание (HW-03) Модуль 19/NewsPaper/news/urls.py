from django.urls import path
from .views import (PostsList,
                    PostDetail,
                    PostSearch,
                    NewsCreate,
                    NewsUpdate,
                    NewsDelete,
                    ArticleCreate,
                    ArticleUpdate,
                    ArticleDelete,
                    )  

urlpatterns = [
    path('', PostsList.as_view(), name='posts_list'),
    path('<int:pk>/', PostDetail.as_view(), name='posts_detail'),
    path('search/', PostSearch.as_view(), name='posts_search'),

    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', NewsUpdate.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),

    path('articles/create/', ArticleCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdate.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
]