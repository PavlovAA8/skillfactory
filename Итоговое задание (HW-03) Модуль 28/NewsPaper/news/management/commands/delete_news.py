from django.core.management.base import BaseCommand
from news.models import Post, Category

class Command(BaseCommand):
    help = 'Удаляет все новости из указанной категории после подтверждения'

    def add_arguments(self, parser):
        parser.add_argument('category_id', type=int, help='ID категории, из которой нужно удалить новости')

    def handle(self, *args, **kwargs):
        category_id = kwargs['category_id']
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('Категория не найдена.'))
            return

        confirmation = input(f'Вы уверены? (y/n):')
        if confirmation.lower() != 'y':
            self.stdout.write(self.style.WARNING('Отмена'))
            return

        deleted_count, _ = Post.objects.filter(postcategory__category=category).delete()
        self.stdout.write(self.style.SUCCESS(f'Удалено {deleted_count} новостей из категории "{category.name}".'))