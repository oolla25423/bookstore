from django.core.management.base import BaseCommand
from api.models import Author, Book, User, Review

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        if Author.objects.exists() or Book.objects.exists() or User.objects.exists():
            self.stdout.write(self.style.WARNING('База данных уже заполнена данными'))
            return

        # Создать авторов
        authors = [
            Author.objects.create(name='Лев Толстой', bio='Русский писатель'),
            Author.objects.create(name='Фёдор Достоевский', bio='Русский писатель'),
            Author.objects.create(name='Александр Пушкин', bio='Русский поэт'),
        ]

        # Создать книги
        books = [
            Book.objects.create(title='Война и мир', author=authors[0], price=500, description='Эпический роман', stock=10),
            Book.objects.create(title='Преступление и наказание', author=authors[1], price=400, description='Психологический роман', stock=8),
            Book.objects.create(title='Евгений Онегин', author=authors[2], price=300, description='Роман в стихах', stock=5),
            Book.objects.create(title='Анна Каренина', author=authors[0], price=450, description='Роман о любви', stock=7),
        ]

        # Создать пользователей
        users = [
            User.objects.create_user(username='admin', email='admin@example.com', password='admin123', role='admin'),
            User.objects.create_user(username='user1', email='user1@example.com', password='user123', role='user'),
            User.objects.create_user(username='user2', email='user2@example.com', password='user123', role='user'),
        ]

        # Создать отзывы
        reviews = [
            Review.objects.create(user=users[1], book=books[0], rating=5, comment='Отличная книга!'),
            Review.objects.create(user=users[2], book=books[1], rating=4, comment='Интересный сюжет.'),
            Review.objects.create(user=users[1], book=books[2], rating=5, comment='Классика!'),
        ]

        self.stdout.write(self.style.SUCCESS('База данных заполнена примерами данных'))