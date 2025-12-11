# -*- coding: utf-8 -*-
"""
Тесты для представлений (Views) и API эндпоинтов
Проверка HTTP-ответов, редиректов, CRUD операций, аутентификации
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.models import Author, Book, Order, OrderItem, Review

User = get_user_model()


class AuthenticationAPITestCase(APITestCase):
    """Тесты для аутентификации через API"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()
        self.register_url = "/api/register/"
        self.login_url = "/api/login/"

    def test_register_user(self):
        """Тест регистрации нового пользователя"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")

    def test_register_user_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "password_confirm": "differentpass",
        }
        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user(self):
        """Тест авторизации пользователя"""
        # Создаем пользователя
        User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Пытаемся войти
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_login_invalid_credentials(self):
        """Тест авторизации с неверными данными"""
        User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookAPITestCase(APITestCase):
    """Тесты для API работы с книгами"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin",
            is_staff=True,
        )
        self.author = Author.objects.create(name="Test Author", bio="Test bio")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            price=Decimal("500.00"),
            description="Test description",
            stock=10,
        )
        self.books_url = "/api/books/"
        self.book_detail_url = f"/api/books/{self.book.id}/"

    def test_list_books_guest(self):
        """Тест получения списка книг гостем (без авторизации)"""
        response = self.client.get(self.books_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_list_books_with_pagination(self):
        """Тест пагинации списка книг"""
        # Создаем дополнительные книги
        for i in range(15):
            Book.objects.create(
                title=f"Book {i}",
                author=self.author,
                price=Decimal("100.00"),
                stock=5,
            )

        response = self.client.get(self.books_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

    def test_get_book_detail(self):
        """Тест получения деталей книги"""
        response = self.client.get(self.book_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Book")
        self.assertEqual(response.data["author"]["name"], "Test Author")

    def test_create_book_authenticated(self):
        """Тест создания книги авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "New Book",
            "author_id": self.author.id,
            "price": "999.99",
            "description": "New book description",
            "stock": 20,
        }
        response = self.client.post(self.books_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Book")
        self.assertTrue(Book.objects.filter(title="New Book").exists())

    def test_create_book_guest(self):
        """Тест создания книги гостем (должен быть запрещен)"""
        data = {
            "title": "New Book",
            "author_id": self.author.id,
            "price": "999.99",
            "stock": 20,
        }
        response = self.client.post(self.books_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_book(self):
        """Тест обновления книги"""
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "Updated Book",
            "author_id": self.author.id,
            "price": "600.00",
            "stock": 15,
        }
        response = self.client.put(self.book_detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Book")

    def test_delete_book(self):
        """Тест удаления книги"""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.book_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())

    def test_search_books(self):
        """Тест поиска книг"""
        Book.objects.create(
            title="War and Peace",
            author=self.author,
            price=Decimal("1500.00"),
            stock=5,
        )

        response = self.client.get(self.books_url, {"search": "War"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)
        self.assertIn("War", response.data["results"][0]["title"])

    def test_filter_books_by_author(self):
        """Тест фильтрации книг по автору"""
        author2 = Author.objects.create(name="Another Author")
        Book.objects.create(
            title="Another Book", author=author2, price=Decimal("300.00"), stock=3
        )

        response = self.client.get(self.books_url, {"author": self.author.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for book in response.data["results"]:
            self.assertEqual(book["author"]["id"], self.author.id)

    def test_ordering_books(self):
        """Тест сортировки книг по цене"""
        Book.objects.create(
            title="Cheap Book", author=self.author, price=Decimal("100.00"), stock=5
        )
        Book.objects.create(
            title="Expensive Book",
            author=self.author,
            price=Decimal("2000.00"),
            stock=2,
        )

        response = self.client.get(self.books_url, {"ordering": "price"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [Decimal(book["price"]) for book in response.data["results"]]
        self.assertEqual(prices, sorted(prices))


class OrderAPITestCase(APITestCase):
    """Тесты для API работы с заказами"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="pass123"
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin",
            is_staff=True,
        )
        self.author = Author.objects.create(name="Test Author")
        self.book1 = Book.objects.create(
            title="Book 1",
            author=self.author,
            price=Decimal("500.00"),
            stock=10,
        )
        self.book2 = Book.objects.create(
            title="Book 2",
            author=self.author,
            price=Decimal("300.00"),
            stock=5,
        )
        self.orders_url = "/api/orders/"
        self.create_order_url = "/api/create-order/"

    def test_create_order_guest(self):
        """Тест создания заказа гостем (должен быть запрещен)"""
        data = {"items": [{"book_id": self.book1.id, "quantity": 1}]}
        response = self.client.post(self.create_order_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_authenticated(self):
        """Тест создания заказа авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)

        data = {
            "items": [
                {"book_id": self.book1.id, "quantity": 2},
                {"book_id": self.book2.id, "quantity": 1},
            ]
        }
        response = self.client.post(self.create_order_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["id"], self.user.id)
        self.assertEqual(len(response.data["items"]), 2)
        self.assertEqual(response.data["total_price"], "1300.00")  # 500*2 + 300*1

    def test_create_order_reduces_stock(self):
        """Тест что создание заказа уменьшает количество на складе"""
        self.client.force_authenticate(user=self.user)

        original_stock = self.book1.stock
        data = {"items": [{"book_id": self.book1.id, "quantity": 3}]}
        response = self.client.post(self.create_order_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.stock, original_stock - 3)

    def test_create_order_insufficient_stock(self):
        """Тест создания заказа при недостаточном количестве товара"""
        self.client.force_authenticate(user=self.user)

        data = {"items": [{"book_id": self.book1.id, "quantity": 100}]}
        response = self.client.post(self.create_order_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_list_orders_user(self):
        """Тест получения списка заказов пользователя"""
        self.client.force_authenticate(user=self.user)

        # Создаем заказы
        order1 = Order.objects.create(user=self.user)
        order2 = Order.objects.create(user=self.other_user)

        response = self.client.get(self.orders_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Пользователь видит только свои заказы
        order_ids = [order["id"] for order in response.data["results"]]
        self.assertIn(order1.id, order_ids)
        self.assertNotIn(order2.id, order_ids)

    def test_list_orders_admin(self):
        """Тест получения всех заказов администратором"""
        self.client.force_authenticate(user=self.admin)

        order1 = Order.objects.create(user=self.user)
        order2 = Order.objects.create(user=self.other_user)

        response = self.client.get(self.orders_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Администратор видит все заказы
        order_ids = [order["id"] for order in response.data["results"]]
        self.assertIn(order1.id, order_ids)
        self.assertIn(order2.id, order_ids)


class ReviewAPITestCase(APITestCase):
    """Тесты для API работы с отзывами"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="pass123"
        )
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            price=Decimal("500.00"),
            stock=10,
        )
        self.reviews_url = "/api/reviews/"

    def test_create_review_guest(self):
        """Тест создания отзыва гостем (должен быть запрещен)"""
        data = {"book_id": self.book.id, "rating": 5, "comment": "Great book!"}
        response = self.client.post(self.reviews_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_authenticated(self):
        """Тест создания отзыва авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)

        data = {"book_id": self.book.id, "rating": 5, "comment": "Excellent!"}
        response = self.client.post(self.reviews_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["user"]["id"], self.user.id)

    def test_list_reviews(self):
        """Тест получения списка отзывов"""
        Review.objects.create(
            user=self.user, book=self.book, rating=5, comment="Great!"
        )
        Review.objects.create(
            user=self.other_user, book=self.book, rating=4, comment="Good!"
        )

        response = self.client.get(self.reviews_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 2)

    def test_filter_reviews_by_book(self):
        """Тест фильтрации отзывов по книге"""
        book2 = Book.objects.create(
            title="Another Book", author=self.author, price=Decimal("300.00"), stock=5
        )

        Review.objects.create(user=self.user, book=self.book, rating=5)
        Review.objects.create(user=self.other_user, book=book2, rating=4)

        response = self.client.get(self.reviews_url, {"book": self.book.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for review in response.data["results"]:
            self.assertEqual(review["book"]["id"], self.book.id)


class ExportAPITestCase(APITestCase):
    """Тесты для экспорта данных в XLSX"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin",
            is_staff=True,
        )
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("500.00"), stock=10
        )
        self.export_url = "/api/export/"

    def test_export_guest(self):
        """Тест экспорта гостем (должен быть запрещен)"""
        response = self.client.get(
            self.export_url, {"model": "book", "fields": ["title", "price"]}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_regular_user(self):
        """Тест экспорта обычным пользователем (должен быть запрещен)"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            self.export_url, {"model": "book", "fields": ["title", "price"]}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_admin(self):
        """Тест экспорта администратором"""
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            self.export_url, {"model": "book", "fields": ["title", "price"]}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("attachment", response["Content-Disposition"])


class HTTPStatusCodesTestCase(TestCase):
    """Тесты HTTP статус-кодов для различных сценариев"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book", author=self.author, price=Decimal("500.00"), stock=10
        )

    def test_404_not_found(self):
        """Тест 404 для несуществующего эндпоинта"""
        response = self.client.get("/api/nonexistent/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_404_book_not_found(self):
        """Тест 404 для несуществующей книги"""
        response = self.client.get("/api/books/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_200_ok_list(self):
        """Тест 200 OK для списка книг"""
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_200_ok_detail(self):
        """Тест 200 OK для детальной страницы"""
        response = self.client.get(f"/api/books/{self.book.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
