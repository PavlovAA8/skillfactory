from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.http import Http404

class PostsList(ListView):
    model = Post
    ordering = ('-data_time_created')
    template_name = 'posts_list.html'
    context_object_name = 'posts_list'
    paginate_by = 10

class PostDetail(DetailView):
    model = Post
    template_name = 'posts_detail.html'
    context_object_name = 'post_detail'

class PostSearch(ListView):
    model = Post
    ordering = ['-data_time_created']
    template_name = 'search.html'
    context_object_name = 'posts_search'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['filter'] = self.filterset
       return context

# Новости

class NewsCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('posts_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'NW'
        post.save()
        form.save_m2m()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type_verbose'] = 'Новость'
        return context

class NewsUpdate(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post_type != 'NW':
            raise Http404("Пост является Статьей. Изменение запрещено!")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('posts_list')

class NewsDelete(DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'

    def get_success_url(self):
        if self.object.post_type == 'NW':
            return reverse_lazy('posts_list')
        else:
            raise Http404("Пост является Статьей. Удаление запрещено!")
        

# Статьи

class ArticleCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('posts_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'AR'
        post.save()
        form.save_m2m()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type_verbose'] = 'Статья'
        return context
    
class ArticleUpdate(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post_type != 'AR':
            raise Http404("Пост является Новостью. Изменение запрещено!")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('posts_list')
        
class ArticleDelete(DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'

    def get_success_url(self):
        if self.object.post_type == 'AR':
            return reverse_lazy('posts_list')
        else:
            raise Http404("Пост является Новостью. Удаление запрещено!")