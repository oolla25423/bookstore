"""
Скрипт для добавления обложек книг
Запуск: Get-Content update_covers.py | docker-compose exec -T web python manage.py shell
"""

from api.models import Book

# Обновляем обложки для каждой книги
updates = [
    ("Война и мир", "https://cv8.litres.ru/pub/c/cover_415/391451.jpg"),
    ("Анна Каренина", "https://cv0.litres.ru/pub/c/cover_415/60819.jpg"),
    ("Преступление и наказание", "https://cv1.litres.ru/pub/c/cover_415/2486451.jpg"),
    ("Идиот", "https://cv3.litres.ru/pub/c/cover_415/2486453.jpg"),
    ("Евгений Онегин", "https://cv7.litres.ru/pub/c/cover_415/163407.jpg"),
    ("Капитанская дочка", "https://cv5.litres.ru/pub/c/cover_415/163405.jpg"),
    ("Мастер и Маргарита", "https://cv4.litres.ru/pub/c/cover_415/159334.jpg"),
    ("Собачье сердце", "https://cv2.litres.ru/pub/c/cover_415/159332.jpg"),
    ("Вишнёвый сад", "https://cv6.litres.ru/pub/c/cover_415/139096.jpg"),
    ("Палата №6", "https://cv8.litres.ru/pub/c/cover_415/139098.jpg"),
    ("Мёртвые души", "https://cv4.litres.ru/pub/c/cover_415/163424.jpg"),
    ("Ревизор", "https://cv2.litres.ru/pub/c/cover_415/163422.jpg"),
    ("Отцы и дети", "https://cv0.litres.ru/pub/c/cover_415/139060.jpg"),
    ("Муму", "https://cv8.litres.ru/pub/c/cover_415/139058.jpg"),
    ("Алые паруса", "https://cv6.litres.ru/pub/c/cover_415/139046.jpg"),
    ("Бегущая по волнам", "https://cv4.litres.ru/pub/c/cover_415/139048.jpg"),
]

print("Начинаем обновление обложек...")
success = 0
failed = 0

for title, url in updates:
    try:
        book = Book.objects.get(title=title)
        book.cover_image = url
        book.save()
        print(f"OK: {title}")
        success += 1
    except Book.DoesNotExist:
        print(f"FAIL: {title} не найдена")
        failed += 1
    except Exception as e:
        print(f"ERROR: {title} - {e}")
        failed += 1

print(f"\nГотово! Успешно: {success}, Ошибок: {failed}")
