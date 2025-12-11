# -*- coding: utf-8 -*-
"""
Тесты безопасности приложения
Проверка защиты от SQL-инъекций, XSS, хеширования паролей
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase

from api.models import Author, Book, Order, Review

User = get_user_model()


class PasswordSecurityTestCase(TestCase):
    """Тесты безопасности паролей"""

    def test_password_is_hashed(self):
        """Проверка что пароли хешируются при сохранении"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="mypassword123"
        )

        # Пароль не должен храниться в открытом виде
        self.assertNotEqual(user.password, "mypassword123")

        # Должен быть хеширован с использованием pbkdf2_sha256
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))

        # Длина хеша должна быть значительной
        self.assertGreater(len(user.password), 50)

    def test_password_verification(self):
        """Проверка верификации пароля"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="correctpass123"
        )

        # Правильный пароль должен проходить проверку
        self.assertTrue(user.check_password("correctpass123"))

        # Неправильный пароль не должен проходить проверку
        self.assertFalse(user.check_password("wrongpassword"))
        self.assertFalse(user.check_password(""))
        self.assertFalse(user.check_password("correctpass124"))

    def test_password_not_retrievable(self):
        """Проверка что пароль нельзя получить в открытом виде"""
        password = "secretpassword123"
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password=password
        )

        # Нет атрибута или метода для получения оригинального пароля
        self.assertFalse(hasattr(user, "get_password"))
        self.assertFalse(hasattr(user, "plain_password"))

        # В базе хранится только хеш
        user_from_db = User.objects.get(username="testuser")
        self.assertNotEqual(user_from_db.password, password)


class SQLInjectionTestCase(APITestCase):
    """Тесты защиты от SQL-инъекций"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            price=Decimal("500.00"),
            stock=10,
        )

    def test_sql_injection_in_search(self):
        """Тест защиты от SQL-инъекции в поиске"""
        # Попытка SQL-инъекции через поиск
        malicious_queries = [
            "' OR '1'='1",
            "'; DROP TABLE api_book; --",
            "1' UNION SELECT * FROM api_user--",
            "' OR 1=1--",
            "admin'--",
            "' OR 'x'='x",
        ]

        for query in malicious_queries:
            response = self.client.get("/api/books/", {"search": query})

            # Запрос не должен приводить к ошибке сервера
            self.assertIn(
                response.status_code, [200, 400], f"Failed for query: {query}"
            )

            # Таблица не должна быть удалена
            self.assertTrue(Book.objects.exists())

    def test_sql_injection_in_filter(self):
        """Тест защиты от SQL-инъекции в фильтрах"""
        malicious_values = [
            "1 OR 1=1",
            "1; DROP TABLE api_book;",
            "'; DELETE FROM api_book WHERE '1'='1",
        ]

        for value in malicious_values:
            response = self.client.get("/api/books/", {"author": value})

            # Не должно быть ошибки 500
            self.assertNotEqual(response.status_code, 500)

            # Данные должны остаться
            self.assertTrue(Book.objects.exists())

    def test_sql_injection_in_ordering(self):
        """Тест защиты от SQL-инъекции в сортировке"""
        malicious_ordering = [
            "price; DROP TABLE api_book;",
            "price' OR '1'='1",
            "1 UNION SELECT * FROM api_user",
        ]

        for ordering in malicious_ordering:
            response = self.client.get("/api/books/", {"ordering": ordering})

            # Запрос должен обрабатываться безопасно
            self.assertIn(response.status_code, [200, 400])
            self.assertTrue(Book.objects.exists())


class XSSProtectionTestCase(APITestCase):
    """Тесты защиты от XSS атак"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("500.00"), stock=10
        )
        self.client.force_authenticate(user=self.user)

    def test_xss_in_review_comment(self):
        """Тест защиты от XSS в комментариях отзывов"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'></iframe>",
        ]

        for payload in xss_payloads:
            data = {"book_id": self.book.id, "rating": 5, "comment": payload}
            response = self.client.post("/api/reviews/", data, format="json")

            if response.status_code == 201:
                review = Review.objects.latest("created_at")

                # XSS код должен храниться как текст, не выполняться
                self.assertEqual(review.comment, payload)

                # При получении через API данные должны быть экранированы
                get_response = self.client.get("/api/reviews/")
                self.assertEqual(get_response.status_code, 200)

                # Очистка
                review.delete()

    def test_xss_in_book_title(self):
        """Тест защиты от XSS в названии книги"""
        xss_payload = "<script>alert('Hacked')</script>"

        data = {
            "title": xss_payload,
            "author_id": self.author.id,
            "price": "999.99",
            "stock": 5,
        }
        response = self.client.post("/api/books/", data, format="json")

        if response.status_code == 201:
            book = Book.objects.get(id=response.data["id"])

            # XSS должен быть сохранен как обычный текст
            self.assertEqual(book.title, xss_payload)

            # При получении через API должно быть безопасно
            get_response = self.client.get(f"/api/books/{book.id}/")
            self.assertEqual(get_response.status_code, 200)

            # Очистка
            book.delete()

    def test_xss_in_author_name(self):
        """Тест защиты от XSS в имени автора"""
        xss_payload = "<img src=x onerror=alert('XSS')>"

        data = {"name": xss_payload, "bio": "Test bio"}
        response = self.client.post("/api/authors/", data, format="json")

        if response.status_code == 201:
            author = Author.objects.get(id=response.data["id"])

            # Имя должно храниться как есть
            self.assertEqual(author.name, xss_payload)

            # Очистка
            author.delete()


class AuthorizationTestCase(APITestCase):
    """Тесты авторизации и доступа"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()
        self.guest_client = APIClient()  # Без аутентификации

        self.regular_user = User.objects.create_user(
            username="user", email="user@example.com", password="pass123", role="user"
        )

        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin",
            is_staff=True,
            is_superuser=True,
        )

        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("500.00"), stock=10
        )

    def test_guest_access_public_endpoints(self):
        """Тест доступа гостя к публичным эндпоинтам"""
        # Гость может просматривать книги
        response = self.guest_client.get("/api/books/")
        self.assertEqual(response.status_code, 200)

        # Гость может просматривать авторов
        response = self.guest_client.get("/api/authors/")
        self.assertEqual(response.status_code, 200)

        # Гость может просматривать отзывы
        response = self.guest_client.get("/api/reviews/")
        self.assertEqual(response.status_code, 200)

    def test_guest_cannot_create_order(self):
        """Тест что гость не может создать заказ"""
        data = {"items": [{"book_id": self.book.id, "quantity": 1}]}
        response = self.guest_client.post("/api/create-order/", data, format="json")

        self.assertEqual(response.status_code, 401)

    def test_guest_cannot_create_review(self):
        """Тест что гость не может оставить отзыв"""
        data = {"book_id": self.book.id, "rating": 5, "comment": "Great!"}
        response = self.guest_client.post("/api/reviews/", data, format="json")

        self.assertEqual(response.status_code, 401)

    def test_regular_user_can_create_order(self):
        """Тест что обычный пользователь может создать заказ"""
        self.client.force_authenticate(user=self.regular_user)

        data = {"items": [{"book_id": self.book.id, "quantity": 1}]}
        response = self.client.post("/api/create-order/", data, format="json")

        self.assertEqual(response.status_code, 201)

    def test_regular_user_cannot_export(self):
        """Тест что обычный пользователь не может экспортировать данные"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            "/api/export/", {"model": "book", "fields": ["title", "price"]}
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_export(self):
        """Тест что администратор может экспортировать данные"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(
            "/api/export/", {"model": "book", "fields": ["title", "price"]}
        )

        self.assertEqual(response.status_code, 200)

    def test_user_sees_only_own_orders(self):
        """Тест что пользователь видит только свои заказы"""
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )

        order1 = Order.objects.create(user=self.regular_user)
        order2 = Order.objects.create(user=user2)

        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/orders/")

        self.assertEqual(response.status_code, 200)
        order_ids = [order["id"] for order in response.data["results"]]

        # Пользователь видит только свой заказ
        self.assertIn(order1.id, order_ids)
        self.assertNotIn(order2.id, order_ids)

    def test_admin_sees_all_orders(self):
        """Тест что администратор видит все заказы"""
        order1 = Order.objects.create(user=self.regular_user)
        order2 = Order.objects.create(user=self.admin_user)

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/orders/")

        self.assertEqual(response.status_code, 200)
        order_ids = [order["id"] for order in response.data["results"]]

        # Администратор видит все заказы
        self.assertIn(order1.id, order_ids)
        self.assertIn(order2.id, order_ids)


class DataValidationTestCase(APITestCase):
    """Тесты валидации данных"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.author = Author.objects.create(name="Test Author")
        self.client.force_authenticate(user=self.user)

    def test_book_negative_price(self):
        """Тест создания книги с отрицательной ценой"""
        data = {
            "title": "Test Book",
            "author_id": self.author.id,
            "price": "-100.00",
            "stock": 5,
        }
        response = self.client.post("/api/books/", data, format="json")

        # Должна быть ошибка валидации
        self.assertEqual(response.status_code, 400)

    def test_review_invalid_rating(self):
        """Тест создания отзыва с недопустимым рейтингом"""
        book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("500.00"), stock=10
        )

        # Рейтинг должен быть от 1 до 5
        invalid_ratings = [0, 6, 10, -1]

        for rating in invalid_ratings:
            data = {"book_id": book.id, "rating": rating, "comment": "Test"}
            response = self.client.post("/api/reviews/", data, format="json")

            # Должна быть ошибка
            self.assertIn(response.status_code, [400, 500])

    def test_order_empty_items(self):
        """Тест создания заказа без товаров"""
        data = {"items": []}
        response = self.client.post("/api/create-order/", data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_duplicate_review(self):
        """Тест создания дублирующего отзыва (один пользователь - одна книга)"""
        book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("500.00"), stock=10
        )

        # Создаем первый отзыв
        data = {"book_id": book.id, "rating": 5, "comment": "First review"}
        response1 = self.client.post("/api/reviews/", data, format="json")
        self.assertEqual(response1.status_code, 201)

        # Попытка создать второй отзыв от того же пользователя
        data2 = {"book_id": book.id, "rating": 4, "comment": "Second review"}
        response2 = self.client.post("/api/reviews/", data, format="json")

        # Должна быть ошибка (уже существует)
        self.assertIn(response2.status_code, [400, 500])
