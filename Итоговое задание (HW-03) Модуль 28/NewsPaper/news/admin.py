from django.contrib import admin
from .models import (Post, 
                     Category, 
                     PostCategory, 
                     Subscriber, 
                     Author, 
                     Comment)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rating')
    search_fields = ('user__username',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'post_type', 'data_time_created', 'author', 'rating')
    list_filter = ('post_type', 'author', 'data_time_created')
    search_fields = ('title', 'text')
    ordering = ('-data_time_created',)

class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'category')
    list_filter = ('category',)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'text', 'data_time_created', 'rating')
    list_filter = ('post', 'user')
    search_fields = ('text',)

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category')
    list_filter = ('category',)
    search_fields = ('user__username',)


admin.site.register(Author, AuthorAdmin) #rating, user_id
admin.site.register(Category, CategoryAdmin) #name
admin.site.register(Post, PostAdmin) #post_type, data_time_created, title, text, rating, author_id
admin.site.register(PostCategory, PostCategoryAdmin) #category_id, post_id
admin.site.register(Comment, CommentAdmin) #text, data_time_created, rating, user_id, post_id
admin.site.register(Subscriber, SubscriberAdmin) #category_id, user_id

