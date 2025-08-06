from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Subscriber, Category, PostCategory
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect,render, get_object_or_404
from django.contrib.auth.models import Group
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .tasks import send_new_post_notification
from django.core.cache import cache
import logging

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
            context['auth'] = True
            in_authors_group = user.groups.filter(name='authors').exists()
            if not in_authors_group:
                context['show_become_author_button'] = True
            
            context['categories'] = Category.objects.all()
            context['subscriptions'] = {category.id: user.subscriptions.filter(category=category).exists() for category in context['categories']}

        return context

class PostDetail(DetailView):
    model = Post
    template_name = 'posts_detail.html'
    context_object_name = 'post_detail'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs): 
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return obj
       
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

        categories = self.request.POST.getlist('category')
        for category_id in categories:
            category = get_object_or_404(Category, id=category_id)
            PostCategory.objects.get_or_create(post=post, category=category)
        return super().form_valid(form)

        # subscribers = Subscriber.objects.filter(category__id__in=categories)
        # for subscriber in subscribers:
        #     context = {
        #         'category_name': category.name,
        #         'post_title': post.title,
        #         'post_text': post.text,
        #         'post_type': 'Новость',
        #         'post_url': self.request.build_absolute_uri(reverse('posts_detail', args=[post.id])),
        #     }
        #     html_content = render_to_string('mail.html', context)

        #     msg = EmailMultiAlternatives(
        #         subject=f'Новый пост в категории {category.name}',
        #         body=f'Проверьте новый пост: {post.title}\n\n{post.text}',
        #         from_email= 'XXX@yandex.ru',     # <-------------------- Почта отправителя
        #         to=[subscriber.user.email],
        #     )
        #     msg.attach_alternative(html_content, "text/html")
        #     msg.send()

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['post_type_verbose'] = 'Новость'
            context['categories'] = Category.objects.all()
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

        categories = self.request.POST.getlist('category')
        for category_id in categories:
            category = get_object_or_404(Category, id=category_id)
            PostCategory.objects.get_or_create(post=post, category=category)
        return super().form_valid(form)

        # subscribers = Subscriber.objects.filter(category__id__in=categories)
        # for subscriber in subscribers:
        #     context = {
        #         'category_name': category.name,
        #         'post_title': post.title,
        #         'post_text': post.text,
        #         'post_type': 'Статья',                
        #         'post_url': self.request.build_absolute_uri(reverse('posts_detail', args=[post.id])),                 
        #     }
        #     html_content = render_to_string('mail.html', context)

        #     msg = EmailMultiAlternatives(
        #         subject=f'Новый пост в категории {category.name}',
        #         body=f'Проверьте новый пост: {post.title}\n\n{post.text}',
        #         from_email= 'XXX@yandex.ru',     # <-------------------- Почта отправителя
        #         to=[subscriber.user.email],
        #     )
        #     msg.attach_alternative(html_content, "text/html")
        #     msg.send()
        # return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type_verbose'] = 'Статья'
        context['categories'] = Category.objects.all()
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

@login_required
def update_subscriptions(request):
    if request.method == 'POST':
        categories = Category.objects.all()

        for category in categories:
            subscription_key = f'subscription_{category.id}'
            if subscription_key in request.POST:
                Subscriber.objects.get_or_create(user=request.user, category=category)
            else:
                Subscriber.objects.filter(user=request.user, category=category).delete()

    return redirect('posts_list')




#Проверка логирования
logger = logging.getLogger('django')
logger_request = logging.getLogger('django.request')
logger_server = logging.getLogger('django.server')
logger_template = logging.getLogger('django.template')
logger_db = logging.getLogger('django.db.backends')
logger_security = logging.getLogger('django.security')


# Тестовые сообщения
logger.debug("Проверка logger DEBUG")
logger.info("Проверка logger INFO")
logger.warning("Проверка logger WARNING")
logger.error("Проверка logger ERROR", exc_info=True)
logger.critical("Проверка logger CRITICAL", exc_info=True)

logger_request.debug("Проверка request DEBUG") # не должно регистрироваться
logger_request.info("Проверка request INFO") # не должно регистрироваться
logger_request.warning("Проверка request WARNING") # не должно регистрироваться
logger_request.error("Проверка request ERROR", exc_info=True)
logger_request.critical("Проверка request CRITICAL", exc_info=True)

logger_server.debug("Проверка server DEBUG") # не должно регистрироваться
logger_server.info("Проверка server INFO") # не должно регистрироваться
logger_server.warning("Проверка server WARNING") # не должно регистрироваться
logger_server.error("Проверка server ERROR", exc_info=True)
logger_server.critical("Проверка server CRITICAL", exc_info=True)

logger_template.debug("Проверка template DEBUG") # не должно регистрироваться
logger_template.info("Проверка template INFO") # не должно регистрироваться
logger_template.warning("Проверка template WARNING") # не должно регистрироваться
logger_template.error("Проверка template ERROR", exc_info=True)
logger_template.critical("Проверка template CRITICAL", exc_info=True)

logger_db.debug("Проверка db DEBUG") # не должно регистрироваться
logger_db.info("Проверка db INFO") # не должно регистрироваться
logger_db.warning("Проверка db WARNING") # не должно регистрироваться
logger_db.error("Проверка db ERROR", exc_info=True)
logger_db.critical("Проверка db CRITICAL", exc_info=True)

logger_security.debug("Проверка security DEBUG") # не должно регистрироваться
logger_security.info("Проверка security INFO")
logger_security.warning("Проверка security WARNING")
logger_security.error("Проверка security ERROR", exc_info=True)
logger_security.critical("Проверка security CRITICAL", exc_info=True)


# Проверка исключения (результат в errors.log)
logger_request.error(f"Проверка деления на 0")
try:
    logger_request.error(f"{1/0}")
except ZeroDivisionError as err:
    logger_request.error("ZeroDivisionError",exc_info=True)