from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Author, Book, Order, OrderItem
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    AuthorSerializer, BookSerializer, OrderSerializer, OrderItemSerializer
)


# Регистрация пользователя
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Авторизация пользователя
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# CRUD для пользователей
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


# CRUD для авторов
class AuthorListCreateView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]


# CRUD для книг
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


# CRUD для заказов
class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


# Создание заказа с элементами
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    items_data = request.data.get('items', [])
    if not items_data:
        return Response({'error': 'Не указаны товары'}, status=status.HTTP_400_BAD_REQUEST)

    total_price = 0
    order_items = []

    for item in items_data:
        book_id = item.get('book_id')
        quantity = item.get('quantity', 1)
        try:
            book = Book.objects.get(id=book_id)
            if book.stock < quantity:
                return Response({'error': f'Недостаточно товара {book.title}'}, status=status.HTTP_400_BAD_REQUEST)
            price = book.price * quantity
            total_price += price
            order_items.append({
                'book': book,
                'quantity': quantity,
                'price': book.price
            })
        except Book.DoesNotExist:
            return Response({'error': f'Книга с id {book_id} не найдена'}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(user=request.user, total_price=total_price)
    for item in order_items:
        OrderItem.objects.create(order=order, book=item['book'], quantity=item['quantity'], price=item['price'])
        item['book'].stock -= item['quantity']
        item['book'].save()

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Экспорт данных в XLSX для администратора
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_data(request):
    if request.user.role != 'admin':
        return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

    model_name = request.GET.get('model')
    fields = request.GET.getlist('fields')

    if not model_name or not fields:
        return Response({'error': 'Укажите model и fields'}, status=status.HTTP_400_BAD_REQUEST)

    models_dict = {
        'user': User,
        'author': Author,
        'book': Book,
        'order': Order,
    }

    if model_name not in models_dict:
        return Response({'error': 'Неверная модель'}, status=status.HTTP_400_BAD_REQUEST)

    model = models_dict[model_name]
    queryset = model.objects.all()

    wb = Workbook()
    ws = wb.active
    ws.title = model_name

    # Заголовки
    for col_num, field in enumerate(fields, 1):
        ws.cell(row=1, column=col_num, value=field)

    # Данные
    for row_num, obj in enumerate(queryset, 2):
        for col_num, field in enumerate(fields, 1):
            value = getattr(obj, field, '')
            ws.cell(row=row_num, column=col_num, value=str(value))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={model_name}.xlsx'
    wb.save(response)
    return response
