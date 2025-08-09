from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Announcement, Comment, AnnouncementImage, ScheduledMessage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy 
from django.contrib.auth.decorators import login_required
from .forms import AnnouncementForm, CommentForm
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from .tasks import send_scheduled_message
from django_filters.views import FilterView
from .filters import CommentFilter
from django.http import HttpResponseForbidden


class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'BB_list.html'
    context_object_name = 'announcement'
    paginate_by = 10

    def get_queryset(self):
        return Announcement.objects.order_by('-created_at')
    
class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = 'announcement_detail.html'
    context_object_name = 'announcement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['form'] = CommentForm()
        return context

class AnnouncementCreate(LoginRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'announcement_form.html'
    success_url = reverse_lazy('announcement_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        images = self.request.FILES.getlist('image')
        for img in images:
            AnnouncementImage.objects.create(announcement=self.object, image=img)

        return response

class AnnouncementUpdate(LoginRequiredMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'announcement_form.html'
    success_url = reverse_lazy('announcement_list')

    def form_valid(self, form):
        response = super().form_valid(form)

        images = self.request.FILES.getlist('image')
        for img in images:
            AnnouncementImage.objects.create(announcement=self.object, image=img)

        return response

class AnnouncementDelete(LoginRequiredMixin, DeleteView):
    model = Announcement
    template_name = 'announcement_confirm_delete.html'
    success_url = reverse_lazy('announcement_list')

    def get_queryset(self):
        return Announcement.objects.filter(author=self.request.user)
    
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'announcement_detail.html'

    def form_valid(self, form):
        announcement = get_object_or_404(Announcement, pk=self.kwargs['pk'])
        form.instance.announcement = announcement
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('announcement_detail', kwargs={'pk': self.kwargs['pk']})

class UserCommentsListView(LoginRequiredMixin, FilterView, ListView):
    model = Comment
    template_name = 'user_comments_list.html'
    context_object_name = 'comments'
    filterset_class = CommentFilter

    def get_queryset(self):
        current_user = self.request.user
        announcements = Announcement.objects.filter(author=current_user)
        queryset = Comment.objects.exclude(user=current_user).filter(announcement__in=announcements).order_by('-created_at')
        
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        selected_comments = request.POST.getlist('selected_comments')
        if action == 'accept':
            for comment_id in selected_comments:
                comment = Comment.objects.get(id=comment_id)
                comment.accepted = True
                comment.save()          
        elif action == 'delete':
            Comment.objects.filter(id__in=selected_comments).delete()

        return redirect('comments', username=request.user.username)
    
class ScheduledMessageCreateView(LoginRequiredMixin, CreateView):
    model = ScheduledMessage
    template_name = 'create_scheduled_message.html'
    fields = ['title', 'content', 'scheduled_time']

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        scheduled_time = form.instance.scheduled_time
        if scheduled_time <= timezone.now():
            send_scheduled_message.delay(form.instance.id)
        else:
            send_scheduled_message.apply_async((form.instance.id,), eta=scheduled_time)

        return response

    def get_success_url(self):
        return reverse_lazy('create_scheduled_message')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = ScheduledMessage.objects.all().order_by('-created_at')
        return context


@login_required
def delete_announcement_image(request, image_id):
    image = get_object_or_404(AnnouncementImage, pk=image_id)
    if image.announcement.author != request.user:
        return HttpResponseForbidden("Вы не можете удалять изображения этого объявления")
    announcement_id = image.announcement.id
    image.delete()
    return redirect('announcement_edit', pk=announcement_id)