from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Author, Book, Order, OrderItem, Review


# Сериализатор для пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# Сериализатор для регистрации
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


# Сериализатор для авторизации
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Неверные учетные данные")
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт не активен")
        data['user'] = user
        return data


# Сериализатор для автора
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


# Сериализатор для книги
class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Book
        fields = '__all__'

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть положительной")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Количество на складе не может быть отрицательным")
        return value


# Сериализатор для элемента заказа
class OrderItemSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть положительным")
        return value


# Сериализатор для заказа
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'total_price']


# Сериализатор для отзыва
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5")
        return value

    def validate(self, data):
        user = self.context['request'].user
        book_id = data.get('book_id')
        if Review.objects.filter(user=user, book_id=book_id).exists():
            raise serializers.ValidationError("Вы уже оставили отзыв на эту книгу")
        return data