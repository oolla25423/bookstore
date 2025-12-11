from django.contrib import admin

from .models import Author, Book, Order, OrderItem, Review, User


# Настройка административной панели для пользователей
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "role", "is_active", "created_at"]
    list_filter = ["role", "is_active", "created_at"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-created_at"]


# Настройка административной панели для авторов
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "updated_at"]
    search_fields = ["name", "bio"]
    ordering = ["name"]


# Настройка административной панели для книг
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "price", "stock", "cover_image", "created_at"]
    list_filter = ["author", "created_at"]
    search_fields = ["title", "description", "author__name"]
    ordering = ["-created_at"]
    readonly_fields = ["cover_image_preview"]

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return f'<img src="{obj.cover_image}" style="max-height: 200px; max-width: 200px;" />'
        return "Нет обложки"

    cover_image_preview.short_description = "Предпросмотр обложки"
    cover_image_preview.allow_tags = True


# Inline для элементов заказа
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["book", "quantity", "price"]


# Настройка административной панели для заказов
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total_price", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__username", "user__email"]
    ordering = ["-created_at"]
    inlines = [OrderItemInline]
    readonly_fields = ["total_price", "created_at", "updated_at"]


# Настройка административной панели для элементов заказа
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "book", "quantity", "price", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["book__title", "order__id"]
    ordering = ["-created_at"]


# Настройка административной панели для отзывов
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "book", "rating", "created_at"]
    list_filter = ["rating", "created_at"]
    search_fields = ["user__username", "book__title", "comment"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
