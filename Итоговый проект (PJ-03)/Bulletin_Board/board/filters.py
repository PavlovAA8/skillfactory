import django_filters
from .models import Comment, Announcement

class CommentFilter(django_filters.FilterSet):
    announcement = django_filters.ModelChoiceFilter(queryset=Announcement.objects.all(), label='Объявление')

    class Meta:
        model = Comment
        fields = ['announcement']