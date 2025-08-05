from django.contrib import admin
from .models import (Post, 
                     Category, 
                     PostCategory, 
                     Subscriber, 
                     Author, 
                     Comment)


admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(PostCategory)
admin.site.register(Comment)
admin.site.register(Subscriber)
# Register your models here.
