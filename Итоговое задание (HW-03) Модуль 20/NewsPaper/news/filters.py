from django_filters import FilterSet, DateFilter
from .models import Post
from django.forms import DateInput

class PostFilter(FilterSet):
   
   data_time_created = DateFilter(
        field_name='data_time_created',
        lookup_expr='gt',
        widget=DateInput(attrs={'type': 'date'}),
        )
   class Meta:
        model = Post
        fields = {
            'title': ['icontains'], 
            'author__user__username': ['icontains'],
        }