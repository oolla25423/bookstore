# -*- coding: utf-8 -*-
"""
Django management команда для заполнения базы данных
Запуск: docker-compose exec web python manage.py populate_db
"""

from django.core.management.base import BaseCommand

from api.models import Author, Book, Order, OrderItem, Review, User


class Command(BaseCommand):
    help = "Заполняет базу данных тестовыми данными"

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("ПОЛНОЕ ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ КНИЖНОГО МАГАЗИНА")
        self.stdout.write("=" * 70)

        # ===== ШАГ 1: СОЗДАНИЕ ПОЛЬЗОВАТЕЛЕЙ =====
        self.stdout.write("\n[1/5] Создание пользователей...")

        users_data = [
            {
                "username": "admin",
                "email": "admin@bookstore.com",
                "password": "admin123",
                "first_name": "Админ",
                "last_name": "Администраторов",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "user1234",
                "first_name": "Иван",
                "last_name": "Иванов",
                "role": "user",
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "password": "user1234",
                "first_name": "Мария",
                "last_name": "Петрова",
                "role": "user",
            },
            {
                "username": "user3",
                "email": "user3@example.com",
                "password": "user1234",
                "first_name": "Алексей",
                "last_name": "Сидоров",
                "role": "user",
            },
        ]

        users = {}
        for user_data in users_data:
            password = user_data.pop("password")
            user, created = User.objects.get_or_create(
                username=user_data["username"], defaults=user_data
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f"  + Создан пользователь: {user.username}")
            else:
                user.set_password(password)
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.save()
                self.stdout.write(f"  ~ Обновлен пользователь: {user.username}")
            users[user_data["username"]] = user

        # ===== ШАГ 2: СОЗДАНИЕ АВТОРОВ =====
        self.stdout.write("\n[2/5] Создание авторов...")

        authors_data = [
            {
                "name": "Лев Толстой",
                "bio": "Русский писатель, публицист, мыслитель. Один из величайших писателей-романистов мира. Автор романов Война и мир и Анна Каренина.",
            },
            {
                "name": "Фёдор Достоевский",
                "bio": "Русский писатель, мыслитель, философ и публицист. Классик мировой литературы. Автор романов Преступление и наказание, Идиот, Братья Карамазовы.",
            },
            {
                "name": "Александр Пушкин",
                "bio": "Русский поэт, драматург и прозаик, заложивший основы русского реалистического направления. Один из самых авторитетных литературных деятелей.",
            },
            {
                "name": "Михаил Булгаков",
                "bio": "Русский писатель, драматург, театральный режиссёр. Автор романов Мастер и Маргарита, Белая гвардия, повести Собачье сердце.",
            },
            {
                "name": "Антон Чехов",
                "bio": "Русский писатель, прозаик, драматург. Один из самых известных драматургов мира. Автор пьес Вишнёвый сад, Три сестры, Чайка.",
            },
            {
                "name": "Николай Гоголь",
                "bio": "Русский прозаик, драматург, поэт, критик, публицист. Классик русской литературы. Автор поэмы Мёртвые души и комедии Ревизор.",
            },
            {
                "name": "Иван Тургенев",
                "bio": "Русский писатель-реалист, поэт, публицист, драматург, переводчик. Один из классиков русской литературы. Автор романа Отцы и дети.",
            },
            {
                "name": "Александр Грин",
                "bio": "Русский писатель-прозаик и поэт, представитель неоромантизма. Автор философско-психологических произведений с элементами символической фантастики.",
            },
        ]

        authors = {}
        for author_data in authors_data:
            author, created = Author.objects.get_or_create(
                name=author_data["name"], defaults={"bio": author_data["bio"]}
            )
            if created:
                self.stdout.write(f"  + Создан автор: {author.name}")
            else:
                author.bio = author_data["bio"]
                author.save()
                self.stdout.write(f"  ~ Обновлен автор: {author.name}")
            authors[author_data["name"]] = author

        # ===== ШАГ 3: СОЗДАНИЕ КНИГ С ОБЛОЖКАМИ =====
        self.stdout.write("\n[3/5] Создание книг с обложками...")

        books_data = [
            {
                "title": "Война и мир",
                "author": "Лев Толстой",
                "price": 1500.00,
                "description": "Роман-эпопея, описывающий события войн против Наполеона: 1805 года и Отечественной 1812 года. Признан одним из величайших произведений мировой литературы.",
                "stock": 15,
                "cover_image": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400&h=600&fit=crop",
            },
            {
                "title": "Анна Каренина",
                "author": "Лев Толстой",
                "price": 1200.00,
                "description": "Роман о трагической любви замужней дамы Анны Карениной и блестящего офицера Вронского на фоне счастливой семейной жизни Константина Левина и Кити Щербацкой.",
                "stock": 20,
                "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
            },
            {
                "title": "Преступление и наказание",
                "author": "Фёдор Достоевский",
                "price": 900.00,
                "description": "Социально-психологический и социально-философский роман. Это глубочайшее психологическое исследование души человека, совершившего преступление.",
                "stock": 25,
                "cover_image": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=400&h=600&fit=crop",
            },
            {
                "title": "Идиот",
                "author": "Фёдор Достоевский",
                "price": 950.00,
                "description": "Роман о князе Мышкине, человеке, который пытается жить по христианским заповедям в современном ему обществе.",
                "stock": 18,
                "cover_image": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=400&h=600&fit=crop",
            },
            {
                "title": "Евгений Онегин",
                "author": "Александр Пушкин",
                "price": 700.00,
                "description": "Роман в стихах, одно из самых значительных произведений русской словесности. Энциклопедия русской жизни по определению Белинского.",
                "stock": 30,
                "cover_image": "https://images.unsplash.com/photo-1524578271613-d550eacf6090?w=400&h=600&fit=crop",
            },
            {
                "title": "Капитанская дочка",
                "author": "Александр Пушкин",
                "price": 600.00,
                "description": "Исторический роман, посвящённый событиям Крестьянской войны 1773–1775 годов под предводительством Емельяна Пугачёва.",
                "stock": 22,
                "cover_image": "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=400&h=600&fit=crop",
            },
            {
                "title": "Мастер и Маргарита",
                "author": "Михаил Булгаков",
                "price": 1100.00,
                "description": "Роман, сочетающий в себе фантастику, сатиру, мистику и философию. История о любви Мастера и Маргариты на фоне визита Воланда в Москву.",
                "stock": 35,
                "cover_image": "https://images.unsplash.com/photo-1491841573634-28140fc7ced7?w=400&h=600&fit=crop",
            },
            {
                "title": "Собачье сердце",
                "author": "Михаил Булгаков",
                "price": 500.00,
                "description": "Повесть о превращении собаки в человека в результате операции, проведенной профессором Преображенским.",
                "stock": 28,
                "cover_image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=600&fit=crop",
            },
            {
                "title": "Вишнёвый сад",
                "author": "Антон Чехов",
                "price": 450.00,
                "description": "Пьеса в четырёх действиях, одна из самых знаменитых пьес в мировой драматургии. История о судьбе дворянской усадьбы.",
                "stock": 12,
                "cover_image": "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400&h=600&fit=crop",
            },
            {
                "title": "Палата №6",
                "author": "Антон Чехов",
                "price": 400.00,
                "description": "Повесть о враче, который попадает в психиатрическую больницу в качестве пациента.",
                "stock": 16,
                "cover_image": "https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=400&h=600&fit=crop",
            },
            {
                "title": "Мёртвые души",
                "author": "Николай Гоголь",
                "price": 850.00,
                "description": "Поэма о похождениях Павла Ивановича Чичикова, авантюриста, скупающего мёртвые души крепостных крестьян.",
                "stock": 19,
                "cover_image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=600&fit=crop",
            },
            {
                "title": "Ревизор",
                "author": "Николай Гоголь",
                "price": 500.00,
                "description": "Комедия в пяти действиях, сатира на нравы чиновничества николаевской России.",
                "stock": 24,
                "cover_image": "https://images.unsplash.com/photo-1589998059171-988d887df646?w=400&h=600&fit=crop",
            },
            {
                "title": "Отцы и дети",
                "author": "Иван Тургенев",
                "price": 750.00,
                "description": "Роман о конфликте поколений, о противостоянии отцов - либеральных дворян и детей - разночинцев-демократов.",
                "stock": 21,
                "cover_image": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&h=600&fit=crop",
            },
            {
                "title": "Муму",
                "author": "Иван Тургенев",
                "price": 300.00,
                "description": "Рассказ о глухонемом дворнике Герасиме и его любви к собаке по кличке Муму.",
                "stock": 40,
                "cover_image": "https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=400&h=600&fit=crop",
            },
            {
                "title": "Алые паруса",
                "author": "Александр Грин",
                "price": 650.00,
                "description": "Феерия о мечте, любви и чуде. История о девушке Ассоль, мечтающей о принце на корабле с алыми парусами.",
                "stock": 26,
                "cover_image": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=400&h=600&fit=crop",
            },
            {
                "title": "Бегущая по волнам",
                "author": "Александр Грин",
                "price": 700.00,
                "description": "Философский роман о поиске смысла жизни, о мечте и реальности.",
                "stock": 14,
                "cover_image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=600&fit=crop",
            },
        ]

        books = {}
        for book_data in books_data:
            author_name = book_data.pop("author")
            book, created = Book.objects.get_or_create(
                title=book_data["title"],
                defaults={**book_data, "author": authors[author_name]},
            )
            if created:
                self.stdout.write(f"  + Создана книга: {book.title}")
            else:
                for key, value in book_data.items():
                    setattr(book, key, value)
                book.author = authors[author_name]
                book.save()
                self.stdout.write(f"  ~ Обновлена книга: {book.title}")
            books[book_data["title"]] = book

        # ===== ШАГ 4: СОЗДАНИЕ ЗАКАЗОВ =====
        self.stdout.write("\n[4/5] Создание заказов...")

        # Удаляем старые заказы для чистоты
        Order.objects.all().delete()

        orders_data = [
            {
                "user": "user1",
                "items": [
                    {"book": "Война и мир", "quantity": 1},
                    {"book": "Мастер и Маргарита", "quantity": 2},
                ],
                "status": "completed",
            },
            {
                "user": "user2",
                "items": [
                    {"book": "Евгений Онегин", "quantity": 1},
                    {"book": "Алые паруса", "quantity": 1},
                ],
                "status": "pending",
            },
            {
                "user": "user3",
                "items": [
                    {"book": "Преступление и наказание", "quantity": 1},
                ],
                "status": "completed",
            },
            {
                "user": "user1",
                "items": [
                    {"book": "Идиот", "quantity": 1},
                    {"book": "Собачье сердце", "quantity": 1},
                    {"book": "Палата №6", "quantity": 1},
                ],
                "status": "pending",
            },
        ]

        for order_data in orders_data:
            user = users[order_data["user"]]
            items = order_data["items"]
            status = order_data["status"]

            order = Order.objects.create(user=user, status=status)

            for item_data in items:
                book = books[item_data["book"]]
                OrderItem.objects.create(
                    order=order,
                    book=book,
                    quantity=item_data["quantity"],
                    price=book.price,
                )

            order.calculate_total()
            self.stdout.write(
                f"  + Создан заказ #{order.id} для пользователя {user.username}"
            )

        # ===== ШАГ 5: СОЗДАНИЕ ОТЗЫВОВ =====
        self.stdout.write("\n[5/5] Создание отзывов...")

        # Удаляем старые отзывы для чистоты
        Review.objects.all().delete()

        reviews_data = [
            {
                "user": "user1",
                "book": "Война и мир",
                "rating": 5,
                "comment": "Великолепное произведение! Читал запоем, несмотря на объём. Толстой - настоящий гений!",
            },
            {
                "user": "user2",
                "book": "Война и мир",
                "rating": 5,
                "comment": "Эпическое полотно русской жизни. Каждый персонаж - живой и многогранный.",
            },
            {
                "user": "user1",
                "book": "Мастер и Маргарита",
                "rating": 5,
                "comment": "Невероятная книга! Переплетение реальности и фантастики завораживает.",
            },
            {
                "user": "user3",
                "book": "Мастер и Маргарита",
                "rating": 5,
                "comment": "Шедевр мировой литературы. Перечитывал много раз и каждый раз нахожу что-то новое.",
            },
            {
                "user": "user2",
                "book": "Преступление и наказание",
                "rating": 5,
                "comment": "Глубокое психологическое исследование. Достоевский - мастер!",
            },
            {
                "user": "user3",
                "book": "Евгений Онегин",
                "rating": 4,
                "comment": "Классика русской литературы. Красивый язык, интересный сюжет.",
            },
            {
                "user": "user1",
                "book": "Алые паруса",
                "rating": 5,
                "comment": "Прекрасная книга о мечте и вере в чудо. Читается легко и с удовольствием.",
            },
            {
                "user": "user2",
                "book": "Собачье сердце",
                "rating": 5,
                "comment": "Сатира Булгакова актуальна и сегодня. Умная и смешная повесть.",
            },
            {
                "user": "user3",
                "book": "Отцы и дети",
                "rating": 4,
                "comment": "Интересное произведение о конфликте поколений. Образ Базарова очень силён.",
            },
            {
                "user": "user1",
                "book": "Капитанская дочка",
                "rating": 5,
                "comment": "Замечательный исторический роман. Пушкин - всегда на высоте!",
            },
            {
                "user": "user2",
                "book": "Мёртвые души",
                "rating": 4,
                "comment": "Гоголевская сатира бессмертна. Очень смешно и очень грустно одновременно.",
            },
            {
                "user": "user3",
                "book": "Идиот",
                "rating": 5,
                "comment": "Трагическая история князя Мышкина. Достоевский показывает, как чистота души обречена в грешном мире.",
            },
        ]

        for review_data in reviews_data:
            user = users[review_data["user"]]
            book = books[review_data["book"]]

            review, created = Review.objects.get_or_create(
                user=user,
                book=book,
                defaults={
                    "rating": review_data["rating"],
                    "comment": review_data["comment"],
                },
            )

            if created:
                self.stdout.write(
                    f"  + Создан отзыв от {user.username} на книгу {book.title}"
                )
            else:
                self.stdout.write(
                    f"  ~ Отзыв от {user.username} на книгу {book.title} уже существует"
                )

        # ===== ИТОГИ =====
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!"))
        self.stdout.write("=" * 70)
        self.stdout.write("\nДанные для входа:")
        self.stdout.write("  Администратор: admin / admin123")
        self.stdout.write("  Пользователь 1: user1 / user1234")
        self.stdout.write("  Пользователь 2: user2 / user1234")
        self.stdout.write("  Пользователь 3: user3 / user1234")
        self.stdout.write("\nСтатистика:")
        self.stdout.write(f"  Пользователей: {User.objects.count()}")
        self.stdout.write(f"  Авторов: {Author.objects.count()}")
        self.stdout.write(f"  Книг: {Book.objects.count()}")
        self.stdout.write(f"  Заказов: {Order.objects.count()}")
        self.stdout.write(f"  Отзывов: {Review.objects.count()}")
        self.stdout.write("\nТеперь вы можете открыть:")
        self.stdout.write("  Frontend: http://localhost:3001")
        self.stdout.write("  Админ-панель: http://localhost:8000/admin/")
        self.stdout.write("  Swagger API: http://localhost:8000/api/schema/swagger-ui/")
        self.stdout.write("=" * 70)
