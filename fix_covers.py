"""
Скрипт для добавления обложек к существующим книгам
Запуск: Get-Content fix_covers.py | docker-compose exec -T web python manage.py shell
"""

from api.models import Book

# Получаем все книги из базы и обновляем обложки
print("=" * 60)
print("Обновление обложек для существующих книг")
print("=" * 60)

# Словарь с обложками
covers = {
    "Война и мир": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Tolstoy_-_War_and_Peace_-_first_edition%2C_1869.jpg/330px-Tolstoy_-_War_and_Peace_-_first_edition%2C_1869.jpg",
    "Анна Каренина": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/AnnaKareninaTitle.jpg/330px-AnnaKareninaTitle.jpg",
    "Преступление и наказание": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Crime_and_Punishment_%28Dostoevsky%29_cover.jpg/330px-Crime_and_Punishment_%28Dostoevsky%29_cover.jpg",
    "Евгений Онегин": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Onegin_1837.jpg/330px-Onegin_1837.jpg",
}

# Обновляем все книги
books = Book.objects.all()
updated = 0
no_cover = 0

for book in books:
    if book.title in covers:
        book.cover_image = covers[book.title]
        book.save()
        print(f"✓ Обложка добавлена: {book.title} (ID: {book.id})")
        updated += 1
    else:
        # Устанавливаем дефолтную обложку
        book.cover_image = (
            "https://via.placeholder.com/300x400/667eea/ffffff?text=Book+Cover"
        )
        book.save()
        print(f"⚠ Дефолтная обложка: {book.title} (ID: {book.id})")
        no_cover += 1

print("=" * 60)
print(f"Результат:")
print(f"  С обложками: {updated}")
print(f"  С дефолтной: {no_cover}")
print(f"  Всего: {books.count()}")
print("=" * 60)
print("\n✓ Готово! Обновите страницу в браузере.")
