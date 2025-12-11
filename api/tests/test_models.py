# -*- coding: utf-8 -*-
"""
Тесты для моделей приложения Bookstore
Проверка создания, валидации, связей и автоматических полей
"""

from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from api.models import Author, Book, Order, OrderItem, Review, User


class BaseModelTestCase(TestCase):
    """Тесты для абстрактной модели BaseModel"""

    def test_created_at_auto_populated(self):
        """Проверка автоматического заполнения created_at"""
        author = Author.objects.create(name="Test Author", bio="Test bio")
        self.assertIsNotNone(author.created_at)
        self.assertLessEqual((timezone.now() - author.created_at).total_seconds(), 2)

    def test_updated_at_auto_populated(self):
        """Проверка автоматического заполнения updated_at"""
        author = Author.objects.create(name="Test Author", bio="Test bio")
        self.assertIsNotNone(author.updated_at)
        self.assertLessEqual((timezone.now() - author.updated_at).total_seconds(), 2)

    def test_updated_at_changes_on_save(self):
        """Проверка обновления updated_at при изменении объекта"""
        author = Author.objects.create(name="Test Author", bio="Test bio")
        original_updated_at = author.updated_at

        # Подождем немного и обновим
        import time

        time.sleep(0.1)
        author.bio = "Updated bio"
        author.save()

        self.assertGreater(author.updated_at, original_updated_at)


class UserModelTestCase(TestCase):
    """Тесты для модели User"""

    def setUp(self):
        """Подготовка данных для тестов"""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_create_user(self):
        """Проверка создания обычного пользователя"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, "user")  # Роль по умолчанию
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Проверка создания суперпользователя"""
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, "admin")

    def test_user_password_hashing(self):
        """Проверка хеширования пароля"""
        user = User.objects.create_user(**self.user_data)
        # Пароль не должен храниться в открытом виде
        self.assertNotEqual(user.password, "testpass123")
        # Должен начинаться с алгоритма хеширования
        self.assertTrue(user.password.startswith("pbkdf2_sha256"))
        # Проверка пароля должна работать
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_user_role_choices(self):
        """Проверка возможных ролей пользователя"""
        roles = ["guest", "user", "admin"]
        for role in roles:
            user = User.objects.create_user(
                username=f"user_{role}",
                email=f"{role}@example.com",
                password="pass123",
                role=role,
            )
            self.assertEqual(user.role, role)

    def test_user_str_method(self):
        """Проверка строкового представления пользователя"""
        user = User.objects.create_user(**self.user_data)
        # По умолчанию __str__ от AbstractUser возвращает username
        self.assertEqual(str(user), "testuser")

    def test_unique_username(self):
        """Проверка уникальности username"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="testuser",  # Дубликат
                email="other@example.com",
                password="pass123",
            )


class AuthorModelTestCase(TestCase):
    """Тесты для модели Author"""

    def test_create_author(self):
        """Проверка создания автора"""
        author = Author.objects.create(name="Leo Tolstoy", bio="Russian writer")
        self.assertEqual(author.name, "Leo Tolstoy")
        self.assertEqual(author.bio, "Russian writer")
        self.assertIsNotNone(author.created_at)
        self.assertIsNotNone(author.updated_at)

    def test_author_str_method(self):
        """Проверка строкового представления автора"""
        author = Author.objects.create(name="Fyodor Dostoevsky")
        self.assertEqual(str(author), "Fyodor Dostoevsky")

    def test_author_bio_optional(self):
        """Проверка что bio необязательное поле"""
        author = Author.objects.create(name="Test Author")
        self.assertEqual(author.bio, "")


class BookModelTestCase(TestCase):
    """Тесты для модели Book"""

    def setUp(self):
        """Подготовка данных для тестов"""
        self.author = Author.objects.create(name="Test Author", bio="Test bio")

    def test_create_book(self):
        """Проверка создания книги"""
        book = Book.objects.create(
            title="Test Book",
            author=self.author,
            price=Decimal("999.99"),
            description="Test description",
            stock=10,
            cover_image="https://example.com/cover.jpg",
        )
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, self.author)
        self.assertEqual(book.price, Decimal("999.99"))
        self.assertEqual(book.stock, 10)

    def test_book_author_relationship(self):
        """Проверка связи книги с автором (ForeignKey)"""
        book1 = Book.objects.create(
            title="Book 1", author=self.author, price=Decimal("100.00")
        )
        book2 = Book.objects.create(
            title="Book 2", author=self.author, price=Decimal("200.00")
        )

        # Проверка обратной связи
        self.assertEqual(self.author.books.count(), 2)
        self.assertIn(book1, self.author.books.all())
        self.assertIn(book2, self.author.books.all())

    def test_book_str_method(self):
        """Проверка строкового представления книги"""
        book = Book.objects.create(
            title="War and Peace", author=self.author, price=Decimal("1500.00")
        )
        self.assertEqual(str(book), "War and Peace")

    def test_book_cascade_delete(self):
        """Проверка каскадного удаления при удалении автора"""
        book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("100.00")
        )
        author_id = self.author.id
        book_id = book.id

        # Удаляем автора
        self.author.delete()

        # Книга тоже должна быть удалена (CASCADE)
        self.assertFalse(Book.objects.filter(id=book_id).exists())

    def test_book_price_decimal(self):
        """Проверка типа и точности поля price"""
        book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("123.45")
        )
        self.assertIsInstance(book.price, Decimal)
        self.assertEqual(book.price, Decimal("123.45"))

    def test_book_stock_positive(self):
        """Проверка что stock должен быть положительным"""
        book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("100.00"), stock=5
        )
        self.assertGreaterEqual(book.stock, 0)


class OrderModelTestCase(TestCase):
    """Тесты для модели Order"""

    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("500.00"), stock=10
        )

    def test_create_order(self):
        """Проверка создания заказа"""
        order = Order.objects.create(
            user=self.user, total_price=Decimal("1000.00"), status="pending"
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_price, Decimal("1000.00"))
        self.assertEqual(order.status, "pending")

    def test_order_user_relationship(self):
        """Проверка связи заказа с пользователем (ForeignKey)"""
        order1 = Order.objects.create(user=self.user)
        order2 = Order.objects.create(user=self.user)

        # Проверка обратной связи
        self.assertEqual(self.user.orders.count(), 2)
        self.assertIn(order1, self.user.orders.all())

    def test_order_status_choices(self):
        """Проверка возможных статусов заказа"""
        statuses = ["pending", "completed", "cancelled"]
        for status_value in statuses:
            order = Order.objects.create(user=self.user, status=status_value)
            self.assertEqual(order.status, status_value)

    def test_order_default_status(self):
        """Проверка статуса по умолчанию"""
        order = Order.objects.create(user=self.user)
        self.assertEqual(order.status, "pending")

    def test_order_calculate_total(self):
        """Проверка расчета общей стоимости заказа"""
        order = Order.objects.create(user=self.user)

        # Добавляем элементы заказа
        OrderItem.objects.create(
            order=order, book=self.book, quantity=2, price=Decimal("500.00")
        )
        OrderItem.objects.create(
            order=order, book=self.book, quantity=1, price=Decimal("500.00")
        )

        # Вызываем метод расчета
        total = order.calculate_total()

        # 2*500 + 1*500 = 1500
        self.assertEqual(total, Decimal("1500.00"))
        self.assertEqual(order.total_price, Decimal("1500.00"))

    def test_order_str_method(self):
        """Проверка строкового представления заказа"""
        order = Order.objects.create(user=self.user)
        expected = f"Заказ {order.id} от testuser"
        self.assertEqual(str(order), expected)


class OrderItemModelTestCase(TestCase):
    """Тесты для модели OrderItem"""

    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("300.00"), stock=10
        )
        self.order = Order.objects.create(user=self.user)

    def test_create_order_item(self):
        """Проверка создания элемента заказа"""
        item = OrderItem.objects.create(
            order=self.order, book=self.book, quantity=3, price=Decimal("300.00")
        )
        self.assertEqual(item.order, self.order)
        self.assertEqual(item.book, self.book)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.price, Decimal("300.00"))

    def test_order_item_relationships(self):
        """Проверка связей элемента заказа"""
        item = OrderItem.objects.create(
            order=self.order, book=self.book, quantity=1, price=self.book.price
        )

        # Проверка обратной связи с заказом
        self.assertEqual(self.order.items.count(), 1)
        self.assertIn(item, self.order.items.all())

    def test_order_item_str_method(self):
        """Проверка строкового представления элемента заказа"""
        item = OrderItem.objects.create(
            order=self.order, book=self.book, quantity=2, price=self.book.price
        )
        expected = f"{self.book.title} x 2"
        self.assertEqual(str(item), expected)


class ReviewModelTestCase(TestCase):
    """Тесты для модели Review"""

    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("500.00")
        )

    def test_create_review(self):
        """Проверка создания отзыва"""
        review = Review.objects.create(
            user=self.user, book=self.book, rating=5, comment="Excellent book!"
        )
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.book, self.book)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Excellent book!")

    def test_review_rating_range(self):
        """Проверка диапазона рейтинга (1-5)"""
        valid_ratings = [1, 2, 3, 4, 5]
        for rating in valid_ratings:
            review = Review.objects.create(
                user=self.user,
                book=self.book,
                rating=rating,
                comment=f"Rating {rating}",
            )
            self.assertIn(review.rating, valid_ratings)
            review.delete()  # Очистка для следующей итерации

    def test_review_unique_together(self):
        """Проверка уникальности (user, book) - один отзыв на книгу"""
        Review.objects.create(
            user=self.user, book=self.book, rating=5, comment="First review"
        )

        # Попытка создать второй отзыв от того же пользователя на ту же книгу
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                user=self.user, book=self.book, rating=4, comment="Second review"
            )

    def test_review_relationships(self):
        """Проверка связей отзыва"""
        review = Review.objects.create(user=self.user, book=self.book, rating=5)

        # Проверка обратных связей
        self.assertIn(review, self.user.reviews.all())
        self.assertIn(review, self.book.reviews.all())

    def test_review_str_method(self):
        """Проверка строкового представления отзыва"""
        review = Review.objects.create(user=self.user, book=self.book, rating=5)
        expected = f"Отзыв testuser на Test Book"
        self.assertEqual(str(review), expected)

    def test_review_comment_optional(self):
        """Проверка что комментарий необязателен"""
        review = Review.objects.create(user=self.user, book=self.book, rating=4)
        self.assertEqual(review.comment, "")


class ModelRelationshipsTestCase(TestCase):
    """Интеграционные тесты для проверки связей между моделями"""

    def setUp(self):
        """Подготовка полного набора данных"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("500.00"), stock=10
        )

    def test_full_order_cycle(self):
        """Тест полного цикла создания заказа"""
        # Создаем заказ
        order = Order.objects.create(user=self.user)

        # Добавляем книги в заказ
        item1 = OrderItem.objects.create(
            order=order, book=self.book, quantity=2, price=self.book.price
        )

        # Проверяем связи
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.user, self.user)
        self.assertEqual(item1.book, self.book)

        # Рассчитываем общую стоимость
        order.calculate_total()
        self.assertEqual(order.total_price, Decimal("1000.00"))

    def test_cascade_delete_order(self):
        """Проверка каскадного удаления элементов при удалении заказа"""
        order = Order.objects.create(user=self.user)
        item = OrderItem.objects.create(
            order=order, book=self.book, quantity=1, price=self.book.price
        )

        item_id = item.id
        order.delete()

        # Элементы заказа должны быть удалены
        self.assertFalse(OrderItem.objects.filter(id=item_id).exists())

    def test_multiple_reviews_different_users(self):
        """Проверка что разные пользователи могут оставлять отзывы на одну книгу"""
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )

        review1 = Review.objects.create(user=self.user, book=self.book, rating=5)
        review2 = Review.objects.create(user=user2, book=self.book, rating=4)

        self.assertEqual(self.book.reviews.count(), 2)
        self.assertIn(review1, self.book.reviews.all())
        self.assertIn(review2, self.book.reviews.all())
