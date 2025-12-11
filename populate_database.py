"""
Полный скрипт для заполнения базы данных книжного магазина
Запуск: Get-Content populate_database.py | docker-compose exec -T web python manage.py shell
"""

from api.models import Author, Book, Order, OrderItem, Review, User

print("=" * 70)
print("ПОЛНОЕ ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ КНИЖНОГО МАГАЗИНА")
print("=" * 70)

# ===== ШАГ 1: СОЗДАНИЕ ПОЛЬЗОВАТЕЛЕЙ =====
print("\n[1/5] Создание пользователей...")

users_data = [
    {
        "username": "admin",
        "email": "admin@bookstore.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "username": "user1",
        "email": "user1@example.com",
        "password": "user1234",
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "role": "user",
    },
    {
        "username": "user2",
        "email": "user2@example.com",
        "password": "user1234",
        "first_name": "Maria",
        "last_name": "Petrova",
        "role": "user",
    },
    {
        "username": "user3",
        "email": "user3@example.com",
        "password": "user1234",
        "first_name": "Alexey",
        "last_name": "Sidorov",
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
        print(f"  + Created user: {user.username}")
    else:
        user.set_password(password)
        for key, value in user_data.items():
            setattr(user, key, value)
        user.save()
        print(f"  ~ Updated user: {user.username}")
    users[user_data["username"]] = user

# ===== ШАГ 2: СОЗДАНИЕ АВТОРОВ =====
print("\n[2/5] Создание авторов...")

authors_data = [
    {
        "name": "Leo Tolstoy",
        "bio": "Russian writer, one of the greatest novelists of all time, author of War and Peace and Anna Karenina.",
    },
    {
        "name": "Fyodor Dostoevsky",
        "bio": "Russian novelist, philosopher, and author of Crime and Punishment and The Brothers Karamazov.",
    },
    {
        "name": "Alexander Pushkin",
        "bio": "Russian poet, playwright, and novelist, considered the founder of modern Russian literature.",
    },
    {
        "name": "Mikhail Bulgakov",
        "bio": "Russian writer and playwright, author of The Master and Margarita.",
    },
    {
        "name": "Anton Chekhov",
        "bio": "Russian playwright and short-story writer, considered one of the greatest writers of all time.",
    },
    {
        "name": "Nikolai Gogol",
        "bio": "Russian dramatist, novelist and short story writer, author of Dead Souls.",
    },
    {
        "name": "Ivan Turgenev",
        "bio": "Russian novelist, short story writer, and playwright, author of Fathers and Sons.",
    },
    {
        "name": "Alexander Grin",
        "bio": "Russian writer, author of romantic novels including Scarlet Sails.",
    },
]

authors = {}
for author_data in authors_data:
    author, created = Author.objects.get_or_create(
        name=author_data["name"], defaults={"bio": author_data["bio"]}
    )
    if created:
        print(f"  + Created author: {author.name}")
    else:
        print(f"  ~ Author exists: {author.name}")
    authors[author_data["name"]] = author

# ===== ШАГ 3: СОЗДАНИЕ КНИГ С ОБЛОЖКАМИ =====
print("\n[3/5] Создание книг с обложками...")

books_data = [
    {
        "title": "War and Peace",
        "author": "Leo Tolstoy",
        "price": 1500.00,
        "description": "Epic novel describing the events of the Napoleonic Wars. One of the greatest works of world literature.",
        "stock": 15,
        "cover_image": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400&h=600&fit=crop",
    },
    {
        "title": "Anna Karenina",
        "author": "Leo Tolstoy",
        "price": 1200.00,
        "description": "A novel about the tragic love of married Anna Karenina and officer Vronsky.",
        "stock": 20,
        "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
    },
    {
        "title": "Crime and Punishment",
        "author": "Fyodor Dostoevsky",
        "price": 900.00,
        "description": "A psychological and philosophical novel about a man who commits murder.",
        "stock": 25,
        "cover_image": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=400&h=600&fit=crop",
    },
    {
        "title": "The Idiot",
        "author": "Fyodor Dostoevsky",
        "price": 950.00,
        "description": "A novel about Prince Myshkin, a man who tries to live by Christian values.",
        "stock": 18,
        "cover_image": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=400&h=600&fit=crop",
    },
    {
        "title": "Eugene Onegin",
        "author": "Alexander Pushkin",
        "price": 700.00,
        "description": "A novel in verse, one of the most significant works of Russian literature.",
        "stock": 30,
        "cover_image": "https://images.unsplash.com/photo-1524578271613-d550eacf6090?w=400&h=600&fit=crop",
    },
    {
        "title": "The Captain's Daughter",
        "author": "Alexander Pushkin",
        "price": 600.00,
        "description": "A historical novel about the Pugachev Rebellion of 1773-1775.",
        "stock": 22,
        "cover_image": "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=400&h=600&fit=crop",
    },
    {
        "title": "The Master and Margarita",
        "author": "Mikhail Bulgakov",
        "price": 1100.00,
        "description": "A novel combining fantasy, satire, mysticism and philosophy.",
        "stock": 35,
        "cover_image": "https://images.unsplash.com/photo-1491841573634-28140fc7ced7?w=400&h=600&fit=crop",
    },
    {
        "title": "Heart of a Dog",
        "author": "Mikhail Bulgakov",
        "price": 500.00,
        "description": "A novella about a dog transformed into a human through surgery.",
        "stock": 28,
        "cover_image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=600&fit=crop",
    },
    {
        "title": "The Cherry Orchard",
        "author": "Anton Chekhov",
        "price": 450.00,
        "description": "A play about the fate of an aristocratic estate.",
        "stock": 12,
        "cover_image": "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400&h=600&fit=crop",
    },
    {
        "title": "Ward No. 6",
        "author": "Anton Chekhov",
        "price": 400.00,
        "description": "A story about a doctor who ends up as a patient in a psychiatric hospital.",
        "stock": 16,
        "cover_image": "https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=400&h=600&fit=crop",
    },
    {
        "title": "Dead Souls",
        "author": "Nikolai Gogol",
        "price": 850.00,
        "description": "A poem about the adventures of Pavel Chichikov buying dead souls.",
        "stock": 19,
        "cover_image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=600&fit=crop",
    },
    {
        "title": "The Inspector General",
        "author": "Nikolai Gogol",
        "price": 500.00,
        "description": "A comedy satirizing the corruption of officials in Tsarist Russia.",
        "stock": 24,
        "cover_image": "https://images.unsplash.com/photo-1589998059171-988d887df646?w=400&h=600&fit=crop",
    },
    {
        "title": "Fathers and Sons",
        "author": "Ivan Turgenev",
        "price": 750.00,
        "description": "A novel about the conflict between generations in 19th century Russia.",
        "stock": 21,
        "cover_image": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&h=600&fit=crop",
    },
    {
        "title": "Mumu",
        "author": "Ivan Turgenev",
        "price": 300.00,
        "description": "A short story about a deaf-mute serf and his love for a dog.",
        "stock": 40,
        "cover_image": "https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=400&h=600&fit=crop",
    },
    {
        "title": "Scarlet Sails",
        "author": "Alexander Grin",
        "price": 650.00,
        "description": "A romantic story about dreams, love and miracles.",
        "stock": 26,
        "cover_image": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=400&h=600&fit=crop",
    },
    {
        "title": "Running on the Waves",
        "author": "Alexander Grin",
        "price": 700.00,
        "description": "A philosophical novel about searching for the meaning of life.",
        "stock": 14,
        "cover_image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=600&fit=crop",
    },
]

books = {}
for book_data in books_data:
    author_name = book_data.pop("author")
    book, created = Book.objects.get_or_create(
        title=book_data["title"], defaults={**book_data, "author": authors[author_name]}
    )
    if created:
        print(f"  + Created book: {book.title}")
    else:
        for key, value in book_data.items():
            setattr(book, key, value)
        book.author = authors[author_name]
        book.save()
        print(f"  ~ Updated book: {book.title}")
    books[book_data["title"]] = book

# ===== ШАГ 4: СОЗДАНИЕ ЗАКАЗОВ =====
print("\n[4/5] Создание заказов...")

# Удаляем старые заказы для чистоты
Order.objects.all().delete()

orders_data = [
    {
        "user": "user1",
        "items": [
            {"book": "War and Peace", "quantity": 1},
            {"book": "The Master and Margarita", "quantity": 2},
        ],
        "status": "completed",
    },
    {
        "user": "user2",
        "items": [
            {"book": "Eugene Onegin", "quantity": 1},
            {"book": "Scarlet Sails", "quantity": 1},
        ],
        "status": "pending",
    },
    {
        "user": "user3",
        "items": [
            {"book": "Crime and Punishment", "quantity": 1},
        ],
        "status": "completed",
    },
    {
        "user": "user1",
        "items": [
            {"book": "The Idiot", "quantity": 1},
            {"book": "Heart of a Dog", "quantity": 1},
            {"book": "Ward No. 6", "quantity": 1},
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
            order=order, book=book, quantity=item_data["quantity"], price=book.price
        )

    order.calculate_total()
    print(f"  + Created order #{order.id} for {user.username}")

# ===== ШАГ 5: СОЗДАНИЕ ОТЗЫВОВ =====
print("\n[5/5] Создание отзывов...")

# Удаляем старые отзывы для чистоты
Review.objects.all().delete()

reviews_data = [
    {
        "user": "user1",
        "book": "War and Peace",
        "rating": 5,
        "comment": "An epic masterpiece! Despite its length, I couldn't put it down. Tolstoy is a true genius!",
    },
    {
        "user": "user2",
        "book": "War and Peace",
        "rating": 5,
        "comment": "An epic canvas of Russian life. Every character is alive and multifaceted.",
    },
    {
        "user": "user1",
        "book": "The Master and Margarita",
        "rating": 5,
        "comment": "An incredible book! The interweaving of reality and fantasy is mesmerizing.",
    },
    {
        "user": "user3",
        "book": "The Master and Margarita",
        "rating": 5,
        "comment": "A masterpiece of world literature. I've reread it many times and always find something new.",
    },
    {
        "user": "user2",
        "book": "Crime and Punishment",
        "rating": 5,
        "comment": "A deep psychological study. Dostoevsky is a master!",
    },
    {
        "user": "user3",
        "book": "Eugene Onegin",
        "rating": 4,
        "comment": "A classic of Russian literature. Beautiful language, interesting plot.",
    },
    {
        "user": "user1",
        "book": "Scarlet Sails",
        "rating": 5,
        "comment": "A wonderful book about dreams and faith in miracles. Easy and enjoyable to read.",
    },
    {
        "user": "user2",
        "book": "Heart of a Dog",
        "rating": 5,
        "comment": "Bulgakov's satire is still relevant today. Smart and funny story.",
    },
    {
        "user": "user3",
        "book": "Fathers and Sons",
        "rating": 4,
        "comment": "An interesting work about the conflict of generations. The image of Bazarov is very strong.",
    },
    {
        "user": "user1",
        "book": "The Captain's Daughter",
        "rating": 5,
        "comment": "A wonderful historical novel. Pushkin is always at his best!",
    },
    {
        "user": "user2",
        "book": "Dead Souls",
        "rating": 4,
        "comment": "Gogol's satire is immortal. Very funny and very sad at the same time.",
    },
    {
        "user": "user3",
        "book": "The Idiot",
        "rating": 5,
        "comment": "The tragic story of Prince Myshkin. Dostoevsky shows how purity of soul is doomed in a sinful world.",
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
        print(f"  + Created review from {user.username} for '{book.title}'")
    else:
        print(f"  ~ Review from {user.username} for '{book.title}' already exists")

# ===== ИТОГИ =====
print("\n" + "=" * 70)
print("DATABASE SUCCESSFULLY POPULATED!")
print("=" * 70)
print("\nLogin credentials:")
print("  Administrator: admin / admin123")
print("  User 1: user1 / user1234")
print("  User 2: user2 / user1234")
print("  User 3: user3 / user1234")
print("\nStatistics:")
print(f"  Users: {User.objects.count()}")
print(f"  Authors: {Author.objects.count()}")
print(f"  Books: {Book.objects.count()}")
print(f"  Orders: {Order.objects.count()}")
print(f"  Reviews: {Review.objects.count()}")
print("\nYou can now access:")
print("  Frontend: http://localhost:3001")
print("  Admin Panel: http://localhost:8000/admin/")
print("  Swagger API: http://localhost:8000/api/schema/swagger-ui/")
print("=" * 70)
