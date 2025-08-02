from django import forms
from .models import Post, Author
        
class PostForm(forms.ModelForm):
    author = forms.ModelChoiceField(queryset=Author.objects.all(), label='Автор')

    class Meta:
        model = Post
        fields = ['title', 'text', 'author']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
        }       