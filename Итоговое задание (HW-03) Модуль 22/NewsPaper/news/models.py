from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from news.resources import POST_TYPES


class Author(models.Model):
    #cвязь «один к одному» с встроенной моделью пользователей User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    #рейтинг пользователя
    rating = models.IntegerField(default=0)

    #Метод update_rating() модели Author, который обновляет рейтинг текущего автора (метод принимает в качестве аргумента только self)
    def update_rating(self):
        # суммарный рейтинг каждой статьи автора умножается на 3
        post_rating = self.post_set.aggregate(total=Sum('rating'))['total'] or 0
        post_rating *= 3

        # суммарный рейтинг всех комментариев автора
        comment_rating = self.user.comment_set.aggregate(total=Sum('rating'))['total'] or 0

        # суммарный рейтинг всех комментариев к статьям автора
        post_comments_rating = Comment.objects.filter(post__author=self).aggregate(total=Sum('rating'))['total'] or 0 
        self.rating = post_rating + comment_rating + post_comments_rating
        self.save()

    def __str__(self):
        # return f'Лучший рейтинг у {self.user.username} - {self.rating}'
        return self.user.username

class Category(models.Model):
    #уникальное название категории
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
        #return f'Лучший рейтинг у {self.user.username} - {self.rating}'

class Post(models.Model):
    #связь «один ко многим» с моделью Author
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    #поле с выбором — «статья» или «новость»
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default='AR')

    #автоматически добавляемая дата и время создания
    data_time_created = models.DateTimeField(auto_now_add=True)

    #связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory)
    categories = models.ManyToManyField(Category, through='PostCategory')

    #заголовок статьи/новости
    title = models.CharField(max_length=255)

    #текст статьи/новости
    text = models.TextField()

    #рейтинг статьи/новости
    rating = models.IntegerField(default=0)

    #Методы like() и dislike(), которые увеличивают/уменьшают рейтинг на единицу
    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    #Метод preview() модели Post, который возвращает начало статьи (предварительный просмотр) длиной 124 символа и добавляет многоточие в конце
    def preview(self):
        return self.text[:124] + '...'

    def __str__(self):
        return self.title
#         return f'''Дата: {self.data_time_created.strftime('%Y-%m-%d %H:%M:%S')}, Автор: {self.author.user.username}, Рейтинг: {self.rating}
# Заголовок: {self.title}
# ({self.get_post_type_display()}) Превью: {self.preview()}'''


class PostCategory(models.Model):
    #связь «один ко многим» с моделью Post
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    #связь «один ко многим» с моделью Category
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post.title} - {self.category.name}'

class Comment(models.Model):
    #связь «один ко многим» с моделью Post
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    #связь «один ко многим» со встроенной моделью User
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    #текст комментария
    text = models.TextField()

    #дата и время создания комментария
    data_time_created = models.DateTimeField(auto_now_add=True)
    
    #рейтинг комментария
    rating = models.IntegerField(default=0)

    #Методы like() и dislike(), которые увеличивают/уменьшают рейтинг на единицу
    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return "\n" + f'''Пользователь {self.user.username} оставил комментарий с текстом "{self.text}".
Дата публикования: {self.data_time_created.strftime('%Y-%m-%d %H:%M:%S')}, Рейтинг: {self.rating}\n'''
    
class Subscriber(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='subscribers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')

    class Meta:
        unique_together = ('category', 'user')
