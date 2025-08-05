from django import forms
from .models import Post, Author, Category
        
class PostForm(forms.ModelForm):
    author = forms.ModelChoiceField(queryset=Author.objects.all(), label='Автор')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label='Категория')

    class Meta:
        model = Post
        fields = ['title', 'text', 'author','category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }       