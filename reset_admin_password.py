"""
Скрипт для сброса пароля администратора
Запуск: Get-Content reset_admin_password.py | docker-compose exec -T web python manage.py shell
"""

from api.models import User

try:
    # Находим администратора
    admin = User.objects.get(username="admin")

    # Устанавливаем новый пароль
    admin.set_password("admin123")
    admin.role = "admin"
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    print("=" * 60)
    print("✓ Пароль администратора успешно сброшен!")
    print("=" * 60)
    print("\nДАННЫЕ ДЛЯ ВХОДА:")
    print("  Логин:    admin")
    print("  Пароль:   admin123")
    print(f"  Email:    {admin.email}")
    print("  Роль:     {0}".format(admin.role))
    print("=" * 60)
    print("\nВы можете войти:")
    print("  Frontend:  http://localhost:3001")
    print("  Swagger:   http://localhost:8000/api/schema/swagger-ui/")
    print("  Админка:   http://localhost:8000/admin/")
    print("=" * 60)

except User.DoesNotExist:
    print("✗ Пользователь 'admin' не найден!")
    print("Создайте его вручную через createsuperuser")
