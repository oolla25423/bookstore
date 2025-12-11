"""
Скрипт для добавления обложек книг
Запуск: Get-Content add_book_covers.py | docker-compose exec -T web python manage.py shell
"""

from api.models import Book

# Словарь с обложками книг (ссылки на изображения)
book_covers = {
    "Война и мир": "https://cv8.litres.ru/pub/c/cover_415/391451.jpg",
    "Анна Каренина": "https://cv0.litres.ru/pub/c/cover_415/60819.jpg",
    "Преступление и наказание": "https://cv1.litres.ru/pub/c/cover_415/2486451.jpg",
    "Идиот": "https://cv3.litres.ru/pub/c/cover_415/2486453.jpg",
    "Евгений Онегин": "https://cv7.litres.ru/pub/c/cover_415/163407.jpg",
    "Капитанская дочка": "https://cv5.litres.ru/pub/c/cover_415/163405.jpg",
    "Мастер и Маргарита": "https://cv4.litres.ru/pub/c/cover_415/159334.jpg",
    "Собачье сердце": "https://cv2.litres.ru/pub/c/cover_415/159332.jpg",
    "Вишнёвый сад": "https://cv6.litres.ru/pub/c/cover_415/139096.jpg",
    "Палата №6": "https://cv8.litres.ru/pub/c/cover_415/139098.jpg",
    "Мёртвые души": "https://cv4.litres.ru/pub/c/cover_415/163424.jpg",
    "Ревизор": "https://cv2.litres.ru/pub/c/cover_415/163422.jpg",
    "Отцы и дети": "https://cv0.litres.ru/pub/c/cover_415/139060.jpg",
    "Муму": "https://cv8.litres.ru/pub/c/cover_415/139058.jpg",
    "Алые паруса": "https://cv6.litres.ru/pub/c/cover_415/139046.jpg",
    "Бегущая по волнам": "https://cv4.litres.ru/pub/c/cover_415/139048.jpg",
}

print("=" * 60)
print("Добавление обложек к книгам...")
print("=" * 60)

updated_count = 0
not_found_count = 0

for title, cover_url in book_covers.items():
    try:
        book = Book.objects.get(title=title)
        book.cover_image = cover_url
        book.save()
        print(f"✓ Обложка добавлена: {title}")
        updated_count += 1
    except Book.DoesNotExist:
        print(f"✗ Книга не найдена: {title}")
        not_found_count += 1

print("=" * 60)
print(f"Результаты:")
print(f"  Обновлено: {updated_count}")
print(f"  Не найдено: {not_found_count}")
print(f"  Всего обработано: {len(book_covers)}")
print("=" * 60)
print("\n✓ Обложки успешно добавлены в базу данных!")
print("Теперь они будут отображаться на сайте.")
