from django.views.generic import ListView, DetailView
from .models import Post

class PostsList(ListView):
    model = Post
    ordering = ('-data_time_created')
    template_name = 'news_list.html'
    context_object_name = 'news_list'

class PostDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'news'