from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserListCreateView)
router.register(r'authors', views.AuthorListCreateView)
router.register(r'books', views.BookListCreateView)
router.register(r'orders', views.OrderListCreateView)

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('create-order/', views.create_order, name='create-order'),
    path('export/', views.export_data, name='export'),
]