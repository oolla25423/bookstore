"""
Скрипт для создания тестовых данных в базе данных книжного магазина.
Запуск: python manage.py shell < create_test_data.py
Или: docker-compose exec web python manage.py shell < create_test_data.py
"""

from django.contrib.auth.hashers import make_password

from api.models import Author, Book, Order, OrderItem, Review, User

# Очистка существующих данных (опционально)
print("Создание тестовых данных...")

# Создание пользователей
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
        print(f"✓ Создан пользователь: {user.username}")
    else:
        print(f"- Пользователь уже существует: {user.username}")
    users[user_data["username"]] = user

# Создание авторов
authors_data = [
    {
        "name": "Лев Толстой",
        "bio": "Русский писатель, публицист, мыслитель, просветитель. Участник обороны Севастополя. Один из наиболее известных русских писателей и мыслителей, один из величайших писателей-романистов мира.",
    },
    {
        "name": "Фёдор Достоевский",
        "bio": "Русский писатель, мыслитель, философ и публицист. Член-корреспондент Петербургской академии наук с 1877 года. Классик мировой литературы, один из самых читаемых русских писателей в мире.",
    },
    {
        "name": "Александр Пушкин",
        "bio": "Русский поэт, драматург и прозаик, заложивший основы русского реалистического направления, критик и теоретик литературы, историк, публицист, один из самых авторитетных литературных деятелей первой трети XIX века.",
    },
    {
        "name": "Михаил Булгаков",
        "bio": "Русский писатель, драматург, театральный режиссёр и актёр. Автор романов, повестей и рассказов, множества фельетонов, пьес, инсценировок, киносценариев, оперных либретто.",
    },
    {
        "name": "Антон Чехов",
        "bio": "Русский писатель, прозаик, драматург, публицист, врач. Почётный академик Императорской Академии наук по разряду изящной словесности. Один из самых известных драматургов мира.",
    },
    {
        "name": "Николай Гоголь",
        "bio": "Русский прозаик, драматург, поэт, критик, публицист, признанный одним из классиков русской литературы. Происходил из старинного дворянского рода Гоголей-Яновских.",
    },
    {
        "name": "Иван Тургенев",
        "bio": "Русский писатель-реалист, поэт, публицист, драматург, переводчик. Один из классиков русской литературы, внёсших наиболее значительный вклад в её развитие во второй половине XIX века.",
    },
    {
        "name": "Александр Грин",
        "bio": "Русский писатель-прозаик и поэт, представитель неоромантизма, автор философско-психологических, с элементами символической фантастики, произведений.",
    },
]

authors = {}
for author_data in authors_data:
    author, created = Author.objects.get_or_create(
        name=author_data["name"], defaults={"bio": author_data["bio"]}
    )
    if created:
        print(f"✓ Создан автор: {author.name}")
    else:
        print(f"- Автор уже существует: {author.name}")
    authors[author_data["name"]] = author

# Создание книг
books_data = [
    {
        "title": "Война и мир",
        "author": "Лев Толстой",
        "price": 1500.00,
        "description": "Роман-эпопея, описывающий события войн против Наполеона: 1805 года и Отечественной 1812 года. Признан одним из величайших произведений мировой литературы.",
        "stock": 15,
    },
    {
        "title": "Анна Каренина",
        "author": "Лев Толстой",
        "price": 1200.00,
        "description": "Роман о трагической любви замужней дамы Анны Карениной и блестящего офицера Вронского на фоне счастливой семейной жизни Константина Левина и Кити Щербацкой.",
        "stock": 20,
    },
    {
        "title": "Преступление и наказание",
        "author": "Фёдор Достоевский",
        "price": 900.00,
        "description": "Социально-психологический и социально-философский роман. Это глубочайшее психологическое исследование души человека, совершившего преступление.",
        "stock": 25,
    },
    {
        "title": "Идиот",
        "author": "Фёдор Достоевский",
        "price": 950.00,
        "description": "Роман о князе Мышкине, человеке, который пытается жить по христианским заповедям в современном ему обществе.",
        "stock": 18,
    },
    {
        "title": "Евгений Онегин",
        "author": "Александр Пушкин",
        "price": 700.00,
        "description": 'Роман в стихах, одно из самых значительных произведений русской словесности. "Энциклопедия русской жизни" по определению Белинского.',
        "stock": 30,
    },
    {
        "title": "Капитанская дочка",
        "author": "Александр Пушкин",
        "price": 600.00,
        "description": "Исторический роман, посвящённый событиям Крестьянской войны 1773–1775 годов под предводительством Емельяна Пугачёва.",
        "stock": 22,
    },
    {
        "title": "Мастер и Маргарита",
        "author": "Михаил Булгаков",
        "price": 1100.00,
        "description": "Роман, сочетающий в себе фантастику, сатиру, мистику и философию. История о любви Мастера и Маргариты на фоне визита Воланда в Москву.",
        "stock": 35,
    },
    {
        "title": "Собачье сердце",
        "author": "Михаил Булгаков",
        "price": 500.00,
        "description": "Повесть о превращении собаки в человека в результате операции, проведенной профессором Преображенским.",
        "stock": 28,
    },
    {
        "title": "Вишнёвый сад",
        "author": "Антон Чехов",
        "price": 450.00,
        "description": "Пьеса в четырёх действиях, одна из самых знаменитых пьес в мировой драматургии. История о судьбе дворянской усадьбы.",
        "stock": 12,
    },
    {
        "title": "Палата №6",
        "author": "Антон Чехов",
        "price": 400.00,
        "description": "Повесть о враче, который попадает в психиатрическую больницу в качестве пациента.",
        "stock": 16,
    },
    {
        "title": "Мёртвые души",
        "author": "Николай Гоголь",
        "price": 850.00,
        "description": "Поэма о похождениях Павла Ивановича Чичикова, авантюриста, скупающего мёртвые души крепостных крестьян.",
        "stock": 19,
    },
    {
        "title": "Ревизор",
        "author": "Николай Гоголь",
        "price": 500.00,
        "description": "Комедия в пяти действиях, сатира на нравы чиновничества николаевской России.",
        "stock": 24,
    },
    {
        "title": "Отцы и дети",
        "author": "Иван Тургенев",
        "price": 750.00,
        "description": 'Роман о конфликте поколений, о противостоянии "отцов" - либеральных дворян и "детей" - разночинцев-демократов.',
        "stock": 21,
    },
    {
        "title": "Муму",
        "author": "Иван Тургенев",
        "price": 300.00,
        "description": "Рассказ о глухонемом дворнике Герасиме и его любви к собаке по кличке Муму.",
        "stock": 40,
    },
    {
        "title": "Алые паруса",
        "author": "Александр Грин",
        "price": 650.00,
        "description": "Феерия о мечте, любви и чуде. История о девушке Ассоль, мечтающей о принце на корабле с алыми парусами.",
        "stock": 26,
    },
    {
        "title": "Бегущая по волнам",
        "author": "Александр Грин",
        "price": 700.00,
        "description": "Философский роман о поиске смысла жизни, о мечте и реальности.",
        "stock": 14,
    },
]

books = {}
for book_data in books_data:
    author_name = book_data.pop("author")
    book, created = Book.objects.get_or_create(
        title=book_data["title"], defaults={**book_data, "author": authors[author_name]}
    )
    if created:
        print(f"✓ Создана книга: {book.title}")
    else:
        print(f"- Книга уже существует: {book.title}")
    books[book_data["title"]] = book

# Создание заказов
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

    # Проверяем, не существует ли уже заказ
    existing_order = Order.objects.filter(user=user, status=status).first()

    if not existing_order:
        order = Order.objects.create(user=user, status=status)

        for item_data in items:
            book = books[item_data["book"]]
            OrderItem.objects.create(
                order=order, book=book, quantity=item_data["quantity"], price=book.price
            )

        order.calculate_total()
        print(f"✓ Создан заказ #{order.id} для пользователя {user.username}")
    else:
        print(f"- Заказ для пользователя {user.username} уже существует")

# Создание отзывов
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
        defaults={"rating": review_data["rating"], "comment": review_data["comment"]},
    )

    if created:
        print(f"✓ Создан отзыв от {user.username} на книгу '{book.title}'")
    else:
        print(f"- Отзыв от {user.username} на книгу '{book.title}' уже существует")

print("\n" + "=" * 50)
print("✅ Создание тестовых данных завершено!")
print("=" * 50)
print("\nТестовые пользователи:")
print("  Администратор: admin / admin123")
print("  Пользователь 1: user1 / user1234")
print("  Пользователь 2: user2 / user1234")
print("  Пользователь 3: user3 / user1234")
print("\nВсего создано:")
print(f"  - Пользователей: {User.objects.count()}")
print(f"  - Авторов: {Author.objects.count()}")
print(f"  - Книг: {Book.objects.count()}")
print(f"  - Заказов: {Order.objects.count()}")
print(f"  - Отзывов: {Review.objects.count()}")
