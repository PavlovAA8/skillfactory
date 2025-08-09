from django import forms
from .models import Announcement, Comment

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['category', 'title', 'content', 'video_url']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

