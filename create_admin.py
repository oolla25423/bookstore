"""
Скрипт для создания администратора
Запуск: python manage.py shell < create_admin.py
"""

from api.models import User

# Проверяем, существует ли администратор
if User.objects.filter(username="admin").exists():
    print("✓ Администратор уже существует")
    admin = User.objects.get(username="admin")
    print(f"  Логин: admin")
    print(f"  Email: {admin.email}")
else:
    # Создаем администратора
    admin = User.objects.create_superuser(
        username="admin",
        email="admin@bookstore.com",
        password="admin123",
        first_name="Администратор",
        last_name="Системы",
        role="admin",
    )
    print("✓ Администратор успешно создан!")
    print("=" * 50)
    print("ДАННЫЕ ДЛЯ ВХОДА:")
    print("  Логин: admin")
    print("  Пароль: admin123")
    print("  Email: admin@bookstore.com")
    print("=" * 50)
    print("\nТеперь вы можете войти:")
    print("  - Frontend: http://localhost:3001")
    print("  - Админка: http://localhost:8000/admin/")
    print("  - Swagger: http://localhost:8000/api/schema/swagger-ui/")
