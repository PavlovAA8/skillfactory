from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Author
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth.models import Group
from django.views.decorators.http import require_POST

class PostsList(ListView):
    model = Post
    ordering = ('-data_time_created')
    template_name = 'posts_list.html'
    context_object_name = 'posts_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['show_become_author_button'] = False

        if user.is_authenticated:
            in_authors_group = user.groups.filter(name='authors').exists()
            if not in_authors_group:
                context['show_become_author_button'] = True

        return context

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

class NewsCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'
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

class NewsUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
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

class NewsDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'news.delete_post'
    model = Post
    template_name = 'post_confirm_delete.html'

    def get_success_url(self):
        if self.object.post_type == 'NW':
            return reverse_lazy('posts_list')
        else:
            raise Http404("Пост является Статьей. Удаление запрещено!")
        

# Статьи

class ArticleCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'
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
    
class ArticleUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
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
        
class ArticleDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'news.delete_post'
    model = Post
    template_name = 'post_confirm_delete.html'

    def get_success_url(self):
        if self.object.post_type == 'AR':
            return reverse_lazy('posts_list')
        else:
            raise Http404("Пост является Новостью. Удаление запрещено!")
        
@login_required
@require_POST
def become_author(request):
    authors_group, created = Group.objects.get_or_create(name='authors')
    request.user.groups.add(authors_group)
    return redirect(request.META.get('HTTP_REFERER', 'posts_list'))
