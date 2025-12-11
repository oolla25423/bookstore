# -*- coding: utf-8 -*-
"""
Интеграционные тесты для полного цикла основных операций
Проверка оформления заказа, работы с корзиной, отзывами
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.models import Author, Book, Order, OrderItem, Review

User = get_user_model()


class OrderFlowIntegrationTestCase(APITestCase):
    """Интеграционные тесты полного цикла оформления заказа"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()

        # Создаем пользователя
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        # Создаем авторов
        self.author1 = Author.objects.create(
            name="Author One", bio="Biography of Author One"
        )
        self.author2 = Author.objects.create(
            name="Author Two", bio="Biography of Author Two"
        )

        # Создаем книги
        self.book1 = Book.objects.create(
            title="Book One",
            author=self.author1,
            description="Description of Book One",
            price=Decimal("500.00"),
            stock=10,
            cover_image="https://example.com/cover1.jpg",
        )
        self.book2 = Book.objects.create(
            title="Book Two",
            author=self.author2,
            description="Description of Book Two",
            price=Decimal("750.00"),
            stock=5,
            cover_image="https://example.com/cover2.jpg",
        )
        self.book3 = Book.objects.create(
            title="Book Three",
            author=self.author1,
            description="Description of Book Three",
            price=Decimal("300.00"),
            stock=20,
        )

    def test_full_order_flow_guest_to_customer(self):
        """
        Полный тест: гость регистрируется, просматривает книги,
        создает заказ и проверяет его
        """
        # Шаг 1: Регистрация нового пользователя
        register_data = {
            "username": "newcustomer",
            "email": "newcustomer@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "Customer",
        }
        response = self.client.post("/api/register/", register_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)

        # Сохраняем токен
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Шаг 2: Просмотр каталога книг
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 3)

        # Шаг 3: Просмотр детальной информации о книге
        response = self.client.get(f"/api/books/{self.book1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Book One")
        self.assertEqual(float(response.data["price"]), 500.00)

        # Шаг 4: Создание заказа с несколькими товарами
        order_data = {
            "items": [
                {"book": self.book1.id, "quantity": 2},
                {"book": self.book2.id, "quantity": 1},
            ]
        }
        response = self.client.post("/api/orders/", order_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order_id = response.data["id"]
        expected_total = (500.00 * 2) + (750.00 * 1)
        self.assertEqual(float(response.data["total_price"]), expected_total)

        # Шаг 5: Проверка что заказ сохранен в БД
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.user.username, "newcustomer")
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.status, "pending")

        # Шаг 6: Просмотр своих заказов
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], order_id)

        # Шаг 7: Просмотр детальной информации о заказе
        response = self.client.get(f"/api/orders/{order_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 2)

        # Шаг 8: Проверка уменьшения stock
        self.book1.refresh_from_db()
        self.book2.refresh_from_db()
        self.assertEqual(self.book1.stock, 8)  # Было 10, заказали 2
        self.assertEqual(self.book2.stock, 4)  # Было 5, заказали 1

    def test_order_flow_with_insufficient_stock(self):
        """Тест оформления заказа с недостаточным количеством товара"""
        self.client.force_authenticate(user=self.user)

        # Пытаемся заказать больше чем в наличии
        order_data = {
            "items": [
                {"book": self.book2.id, "quantity": 10}  # В наличии только 5
            ]
        }
        response = self.client.post("/api/orders/", order_data, format="json")

        # Должна быть ошибка валидации
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "stock",
            str(response.data).lower() or "quantity",
            str(response.data).lower(),
        )

    def test_order_flow_multiple_orders(self):
        """Тест создания нескольких заказов одним пользователем"""
        self.client.force_authenticate(user=self.user)

        # Первый заказ
        order1_data = {"items": [{"book": self.book1.id, "quantity": 1}]}
        response1 = self.client.post("/api/orders/", order1_data, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Второй заказ
        order2_data = {"items": [{"book": self.book2.id, "quantity": 2}]}
        response2 = self.client.post("/api/orders/", order2_data, format="json")
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # Проверяем что оба заказа созданы
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_order_isolation_between_users(self):
        """Тест что пользователи видят только свои заказы"""
        # Создаем второго пользователя
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )

        # Первый пользователь создает заказ
        self.client.force_authenticate(user=self.user)
        order_data = {"items": [{"book": self.book1.id, "quantity": 1}]}
        response = self.client.post("/api/orders/", order_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Второй пользователь не должен видеть заказ первого
        self.client.force_authenticate(user=user2)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

        # Второй пользователь создает свой заказ
        order_data2 = {"items": [{"book": self.book2.id, "quantity": 1}]}
        response = self.client.post("/api/orders/", order_data2, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Теперь второй пользователь видит только свой заказ
        response = self.client.get("/api/orders/")
        self.assertEqual(len(response.data["results"]), 1)


class ReviewFlowIntegrationTestCase(APITestCase):
    """Интеграционные тесты работы с отзывами"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="reviewer", email="reviewer@example.com", password="pass123"
        )

        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            price=Decimal("500.00"),
            stock=10,
        )

    def test_full_review_flow(self):
        """Полный цикл: покупка книги и оставление отзыва"""
        self.client.force_authenticate(user=self.user)

        # Шаг 1: Создаем заказ с книгой
        order_data = {"items": [{"book": self.book.id, "quantity": 1}]}
        response = self.client.post("/api/orders/", order_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Шаг 2: Оставляем отзыв на книгу
        review_data = {
            "book": self.book.id,
            "rating": 5,
            "comment": "Excellent book! Highly recommend.",
        }
        response = self.client.post("/api/reviews/", review_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review_id = response.data["id"]

        # Шаг 3: Проверяем что отзыв отображается
        response = self.client.get(f"/api/books/{self.book.id}/reviews/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

        # Шаг 4: Проверяем детали отзыва
        response = self.client.get(f"/api/reviews/{review_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["comment"], "Excellent book! Highly recommend.")

    def test_cannot_review_same_book_twice(self):
        """Тест что нельзя оставить два отзыва на одну книгу"""
        self.client.force_authenticate(user=self.user)

        # Первый отзыв
        review_data = {"book": self.book.id, "rating": 5, "comment": "Great!"}
        response = self.client.post("/api/reviews/", review_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Попытка оставить второй отзыв
        review_data2 = {"book": self.book.id, "rating": 4, "comment": "Still good"}
        response = self.client.post("/api/reviews/", review_data2, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_users_can_review_same_book(self):
        """Тест что разные пользователи могут оставлять отзывы на одну книгу"""
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )

        # Первый пользователь оставляет отзыв
        self.client.force_authenticate(user=self.user)
        review_data1 = {"book": self.book.id, "rating": 5, "comment": "Excellent!"}
        response = self.client.post("/api/reviews/", review_data1, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Второй пользователь оставляет свой отзыв
        self.client.force_authenticate(user=user2)
        review_data2 = {"book": self.book.id, "rating": 4, "comment": "Good book"}
        response = self.client.post("/api/reviews/", review_data2, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем что оба отзыва есть
        response = self.client.get(f"/api/books/{self.book.id}/reviews/")
        self.assertEqual(len(response.data["results"]), 2)


class SearchFilterIntegrationTestCase(APITestCase):
    """Интеграционные тесты поиска и фильтрации"""

    def setUp(self):
        """Подготовка данных"""
        self.client = APIClient()

        # Создаем авторов
        self.author1 = Author.objects.create(name="John Smith")
        self.author2 = Author.objects.create(name="Jane Doe")

        # Создаем книги с разными характеристиками
        self.python_book = Book.objects.create(
            title="Python Programming",
            author=self.author1,
            price=Decimal("500.00"),
            stock=10,
            description="Learn Python from scratch",
        )
        self.django_book = Book.objects.create(
            title="Django Web Development",
            author=self.author1,
            price=Decimal("700.00"),
            stock=5,
            description="Master Django framework",
        )
        self.javascript_book = Book.objects.create(
            title="JavaScript Basics",
            author=self.author2,
            price=Decimal("400.00"),
            stock=15,
            description="Introduction to JavaScript",
        )

    def test_search_by_title(self):
        """Тест поиска книг по названию"""
        response = self.client.get("/api/books/", {"search": "Python"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Python Programming")

    def test_search_by_author_name(self):
        """Тест поиска книг по имени автора"""
        response = self.client.get("/api/books/", {"search": "John"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 2)  # Python и Django книги

    def test_filter_by_author(self):
        """Тест фильтрации книг по автору"""
        response = self.client.get("/api/books/", {"author": self.author2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "JavaScript Basics")

    def test_filter_by_price_range(self):
        """Тест фильтрации по диапазону цен"""
        response = self.client.get(
            "/api/books/", {"price_min": "450", "price_max": "600"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Python Programming")

    def test_ordering_by_price(self):
        """Тест сортировки по цене"""
        # По возрастанию
        response = self.client.get("/api/books/", {"ordering": "price"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        prices = [float(book["price"]) for book in results]
        self.assertEqual(prices, sorted(prices))

        # По убыванию
        response = self.client.get("/api/books/", {"ordering": "-price"})
        results = response.data["results"]
        prices = [float(book["price"]) for book in results]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_combined_search_and_filter(self):
        """Тест комбинированного поиска и фильтрации"""
        response = self.client.get(
            "/api/books/",
            {"search": "Python", "price_min": "400", "ordering": "-price"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("Python", results[0]["title"])


class DatabaseStateIntegrationTestCase(APITestCase):
    """Тесты изменения состояния БД при операциях"""

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

    def test_database_state_after_order(self):
        """Проверка состояния БД после создания заказа"""
        self.client.force_authenticate(user=self.user)

        initial_orders_count = Order.objects.count()
        initial_order_items_count = OrderItem.objects.count()
        initial_stock = self.book.stock

        # Создаем заказ
        order_data = {"items": [{"book": self.book.id, "quantity": 3}]}
        response = self.client.post("/api/orders/", order_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем изменения в БД
        self.assertEqual(Order.objects.count(), initial_orders_count + 1)
        self.assertEqual(OrderItem.objects.count(), initial_order_items_count + 1)

        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, initial_stock - 3)

    def test_database_state_after_review(self):
        """Проверка состояния БД после создания отзыва"""
        self.client.force_authenticate(user=self.user)

        initial_reviews_count = Review.objects.count()

        # Создаем отзыв
        review_data = {"book": self.book.id, "rating": 5, "comment": "Great book!"}
        response = self.client.post("/api/reviews/", review_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем изменения в БД
        self.assertEqual(Review.objects.count(), initial_reviews_count + 1)

        # Проверяем связь отзыва с пользователем и книгой
        review = Review.objects.latest("created_at")
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.book, self.book)

    def test_cascade_delete_order_items(self):
        """Проверка каскадного удаления OrderItem при удалении Order"""
        self.client.force_authenticate(user=self.user)

        # Создаем заказ
        order_data = {"items": [{"book": self.book.id, "quantity": 2}]}
        response = self.client.post("/api/orders/", order_data, format="json")
        order_id = response.data["id"]

        order = Order.objects.get(id=order_id)
        order_items_count = order.items.count()
        self.assertGreater(order_items_count, 0)

        initial_items_count = OrderItem.objects.count()

        # Удаляем заказ
        order.delete()

        # Проверяем что OrderItem также удалены
        self.assertEqual(
            OrderItem.objects.count(), initial_items_count - order_items_count
        )
