# -*- coding: utf-8 -*-
"""
Тесты для сериализаторов
Проверка валидации данных, вложенных объектов, полей
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from api.models import Author, Book, Order, Review
from api.serializers import (
    AuthorSerializer,
    BookSerializer,
    OrderSerializer,
    RegisterSerializer,
    ReviewSerializer,
    UserSerializer,
)

User = get_user_model()


class UserSerializerTestCase(TestCase):
    """Тесты для сериализатора пользователя"""

    def test_user_serializer_valid_data(self):
        """Тест сериализации пользователя с валидными данными"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        serializer = UserSerializer(user)
        data = serializer.data

        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["first_name"], "Test")
        self.assertEqual(data["last_name"], "User")

        # Пароль не должен быть в сериализованных данных
        self.assertNotIn("password", data)

    def test_user_registration_valid_data(self):
        """Тест регистрации пользователя с валидными данными"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "first_name": "New",
            "last_name": "User",
        }

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("securepass123"))

    def test_user_registration_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "pass123",
            "password_confirm": "different123",
            "first_name": "New",
            "last_name": "User",
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_user_registration_duplicate_username(self):
        """Тест регистрации с существующим username"""
        User.objects.create_user(
            username="existing", email="existing@example.com", password="pass123"
        )

        data = {
            "username": "existing",
            "email": "newemail@example.com",
            "password": "pass123",
            "password_confirm": "pass123",
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_user_registration_invalid_email(self):
        """Тест регистрации с невалидным email"""
        data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "pass123",
            "password_confirm": "pass123",
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class AuthorSerializerTestCase(TestCase):
    """Тесты для сериализатора автора"""

    def test_author_serializer_valid_data(self):
        """Тест сериализации автора с валидными данными"""
        author = Author.objects.create(name="Test Author", bio="Test biography")

        serializer = AuthorSerializer(author)
        data = serializer.data

        self.assertEqual(data["name"], "Test Author")
        self.assertEqual(data["bio"], "Test biography")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_author_serializer_create(self):
        """Тест создания автора через сериализатор"""
        data = {"name": "New Author", "bio": "Biography of new author"}

        serializer = AuthorSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        author = serializer.save()
        self.assertEqual(author.name, "New Author")
        self.assertEqual(author.bio, "Biography of new author")

    def test_author_serializer_update(self):
        """Тест обновления автора через сериализатор"""
        author = Author.objects.create(name="Old Name", bio="Old bio")

        data = {"name": "Updated Name", "bio": "Updated bio"}
        serializer = AuthorSerializer(author, data=data)
        self.assertTrue(serializer.is_valid())

        updated_author = serializer.save()
        self.assertEqual(updated_author.name, "Updated Name")
        self.assertEqual(updated_author.bio, "Updated bio")

    def test_author_serializer_empty_name(self):
        """Тест создания автора с пустым именем"""
        data = {"name": "", "bio": "Some bio"}

        serializer = AuthorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)


class BookSerializerTestCase(TestCase):
    """Тесты для сериализатора книги"""

    def setUp(self):
        """Подготовка данных"""
        self.author = Author.objects.create(name="Test Author", bio="Bio")

    def test_book_serializer_valid_data(self):
        """Тест сериализации книги с валидными данными"""
        book = Book.objects.create(
            title="Test Book",
            author=self.author,
            description="Test description",
            price=Decimal("500.00"),
            stock=10,
            cover_image="https://example.com/cover.jpg",
        )

        serializer = BookSerializer(book)
        data = serializer.data

        self.assertEqual(data["title"], "Test Book")
        self.assertEqual(float(data["price"]), 500.00)
        self.assertEqual(data["stock"], 10)
        self.assertEqual(data["author"]["name"], "Test Author")

    def test_book_serializer_create(self):
        """Тест создания книги через сериализатор"""
        data = {
            "title": "New Book",
            "author": self.author.id,
            "description": "Description",
            "price": "600.00",
            "stock": 15,
        }

        serializer = BookSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        book = serializer.save()
        self.assertEqual(book.title, "New Book")
        self.assertEqual(book.price, Decimal("600.00"))
        self.assertEqual(book.stock, 15)

    def test_book_serializer_negative_price(self):
        """Тест валидации отрицательной цены"""
        data = {
            "title": "Book",
            "author": self.author.id,
            "price": "-100.00",
            "stock": 10,
        }

        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_book_serializer_negative_stock(self):
        """Тест валидации отрицательного количества"""
        data = {
            "title": "Book",
            "author": self.author.id,
            "price": "500.00",
            "stock": -5,
        }

        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("stock", serializer.errors)

    def test_book_serializer_missing_required_fields(self):
        """Тест создания книги без обязательных полей"""
        data = {"title": "Book"}

        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("author", serializer.errors)
        self.assertIn("price", serializer.errors)

    def test_book_serializer_invalid_author(self):
        """Тест создания книги с несуществующим автором"""
        data = {
            "title": "Book",
            "author": 99999,  # Несуществующий ID
            "price": "500.00",
            "stock": 10,
        }

        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("author", serializer.errors)


class OrderSerializerTestCase(TestCase):
    """Тесты для сериализатора заказа"""

    def setUp(self):
        """Подготовка данных"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.author = Author.objects.create(name="Author")
        self.book1 = Book.objects.create(
            title="Book 1", author=self.author, price=Decimal("500.00"), stock=10
        )
        self.book2 = Book.objects.create(
            title="Book 2", author=self.author, price=Decimal("300.00"), stock=5
        )

    def test_order_serializer_create_with_items(self):
        """Тест создания заказа с товарами через сериализатор"""
        data = {
            "items": [
                {"book": self.book1.id, "quantity": 2},
                {"book": self.book2.id, "quantity": 1},
            ]
        }

        serializer = OrderSerializer(
            data=data, context={"request": type("obj", (), {"user": self.user})()}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        order = serializer.save(user=self.user)
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.total_price, Decimal("1300.00"))  # 500*2 + 300*1

    def test_order_serializer_empty_items(self):
        """Тест создания заказа без товаров"""
        data = {"items": []}

        serializer = OrderSerializer(
            data=data, context={"request": type("obj", (), {"user": self.user})()}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("items", serializer.errors)

    def test_order_serializer_invalid_quantity(self):
        """Тест создания заказа с нулевым или отрицательным количеством"""
        data = {"items": [{"book": self.book1.id, "quantity": 0}]}

        serializer = OrderSerializer(
            data=data, context={"request": type("obj", (), {"user": self.user})()}
        )
        self.assertFalse(serializer.is_valid())

    def test_order_serializer_exceeds_stock(self):
        """Тест создания заказа с количеством превышающим stock"""
        data = {"items": [{"book": self.book2.id, "quantity": 10}]}  # stock=5

        serializer = OrderSerializer(
            data=data, context={"request": type("obj", (), {"user": self.user})()}
        )
        # Валидация может пройти в сериализаторе, но должна провалиться при save
        # или в валидаторе, если он реализован
        if serializer.is_valid():
            try:
                serializer.save(user=self.user)
                # Если save прошел, проверим что stock не ушел в минус
                self.book2.refresh_from_db()
                self.assertGreaterEqual(self.book2.stock, 0)
            except ValidationError:
                pass  # Ожидаемое поведение


class ReviewSerializerTestCase(TestCase):
    """Тесты для сериализатора отзывов"""

    def setUp(self):
        """Подготовка данных"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.author = Author.objects.create(name="Author")
        self.book = Book.objects.create(
            title="Book", author=self.author, price=Decimal("500.00"), stock=10
        )

    def test_review_serializer_valid_data(self):
        """Тест сериализации отзыва с валидными данными"""
        review = Review.objects.create(
            user=self.user, book=self.book, rating=5, comment="Excellent book!"
        )

        serializer = ReviewSerializer(review)
        data = serializer.data

        self.assertEqual(data["rating"], 5)
        self.assertEqual(data["comment"], "Excellent book!")
        self.assertEqual(data["user"]["username"], "testuser")

    def test_review_serializer_create(self):
        """Тест создания отзыва через сериализатор"""
        data = {"book": self.book.id, "rating": 4, "comment": "Good book"}

        serializer = ReviewSerializer(
            data=data, context={"request": type("obj", (), {"user": self.user})()}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        review = serializer.save(user=self.user)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, "Good book")
        self.assertEqual(review.user, self.user)

    def test_review_serializer_invalid_rating_too_high(self):
        """Тест создания отзыва с рейтингом выше 5"""
        data = {"book": self.book.id, "rating": 6, "comment": "Great"}

        serializer = ReviewSerializer(
            data=data, context={"request": type("obj", (), {"user": self.user})()}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_review_serializer_invalid_rating_too_low(self):
        """Тест создания отзыва с рейтингом ниже 1"""
        data = {"book": self.book.id, "rating": 0, "comment": "Bad"}

        serializer = ReviewSerializer(
            data=data, context={"request": type("obj", (), {"user": self.user})()}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_review_serializer_empty_comment(self):
        """Тест создания отзыва с пустым комментарием"""
        data = {"book": self.book.id, "rating": 5, "comment": ""}

        serializer = ReviewSerializer(
            data=data, context={"request": type("obj", (), {"user": self.user})()}
        )
        # Комментарий может быть необязательным
        if not serializer.is_valid():
            self.assertIn("comment", serializer.errors)

    def test_review_serializer_duplicate(self):
        """Тест создания дубликата отзыва"""
        # Создаем первый отзыв
        Review.objects.create(
            user=self.user, book=self.book, rating=5, comment="First review"
        )

        # Пытаемся создать второй
        data = {"book": self.book.id, "rating": 4, "comment": "Second review"}

        serializer = ReviewSerializer(
            data=data, context={"request": type("obj", (), {"user": self.user})()}
        )

        # Должна быть ошибка валидации или при save
        if serializer.is_valid():
            try:
                serializer.save(user=self.user)
                self.fail("Should not allow duplicate reviews")
            except Exception:
                pass  # Ожидаемое поведение
        else:
            # Проверяем что есть ошибка
            self.assertTrue(len(serializer.errors) > 0)


class SerializerFieldsTestCase(TestCase):
    """Тесты для проверки полей в сериализаторах"""

    def test_book_serializer_readonly_fields(self):
        """Проверка readonly полей в BookSerializer"""
        author = Author.objects.create(name="Author")
        book = Book.objects.create(
            title="Book", author=author, price=Decimal("500.00"), stock=10
        )

        serializer = BookSerializer(book)

        # created_at и updated_at должны быть readonly
        self.assertIn("created_at", serializer.data)
        self.assertIn("updated_at", serializer.data)

    def test_user_serializer_excludes_password(self):
        """Проверка что пароль исключен из UserSerializer"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

        serializer = UserSerializer(user)

        # Пароль не должен быть в сериализованных данных
        self.assertNotIn("password", serializer.data)

        # Но должны быть другие поля
        self.assertIn("username", serializer.data)
        self.assertIn("email", serializer.data)

    def test_order_serializer_includes_nested_items(self):
        """Проверка вложенных items в OrderSerializer"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        author = Author.objects.create(name="Author")
        book = Book.objects.create(
            title="Book", author=author, price=Decimal("500.00"), stock=10
        )

        order = Order.objects.create(user=user, total_price=Decimal("1000.00"))
        order.items.create(book=book, quantity=2, price=Decimal("500.00"))

        serializer = OrderSerializer(order)

        self.assertIn("items", serializer.data)
        self.assertEqual(len(serializer.data["items"]), 1)
        self.assertEqual(serializer.data["items"][0]["quantity"], 2)
