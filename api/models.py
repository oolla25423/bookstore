from django.db import models
from django.contrib.auth.models import AbstractUser


# Абстрактная базовая модель с полями created_at и updated_at
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        abstract = True

# Пользовательская модель пользователя с ролями
class User(AbstractUser, BaseModel):
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name="Роль")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


# Модель автора
class Author(BaseModel):
    name = models.CharField(max_length=100, verbose_name="Имя автора")
    bio = models.TextField(blank=True, verbose_name="Биография")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"


# Модель книги
class Book(BaseModel):
    title = models.CharField(max_length=200, verbose_name="Название")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books', verbose_name="Автор")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(blank=True, verbose_name="Описание")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"


# Модель заказа
class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая цена")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Ожидает'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен')
    ], default='pending', verbose_name="Статус")

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


# Промежуточная модель для элементов заказа
class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
