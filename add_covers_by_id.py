"""
Скрипт для добавления обложек книг по ID (без использования кириллицы)
Запуск: Get-Content add_covers_by_id.py | docker-compose exec -T web python manage.py shell
"""

from api.models import Book

print("=" * 60)
print("Adding book covers...")
print("=" * 60)

# Получаем все книги и добавляем обложки
books = Book.objects.all().order_by("id")

# Обложки для книг (используем качественные изображения)
cover_urls = [
    "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400",  # Book 1
    "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400",  # Book 2
    "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=400",  # Book 3
    "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=400",  # Book 4
    "https://images.unsplash.com/photo-1524578271613-d550eacf6090?w=400",  # Book 5
    "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=400",  # Book 6
    "https://images.unsplash.com/photo-1491841573634-28140fc7ced7?w=400",  # Book 7
    "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400",  # Book 8
]

updated = 0
for i, book in enumerate(books):
    if i < len(cover_urls):
        book.cover_image = cover_urls[i]
    else:
        # Для дополнительных книг используем placeholder
        book.cover_image = (
            f"https://via.placeholder.com/400x600/667eea/ffffff?text=Book+{book.id}"
        )

    book.save()
    print(f"Updated book ID {book.id}: {book.cover_image[:50]}...")
    updated += 1

print("=" * 60)
print(f"Total updated: {updated} books")
print("=" * 60)
print("\nDone! Refresh your browser to see the covers.")
print("Admin: http://localhost:8000/admin/api/book/")
print("Frontend: http://localhost:3001")
