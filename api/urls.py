from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="Bookstore API",
        default_version="v1",
        description="API для книжного магазина с JWT аутентификацией. Для авторизации нажмите кнопку 'Authorize' и введите: Bearer <ваш_токен>",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@bookstore.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("users/", views.UserListCreateView.as_view(), name="user-list"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("authors/", views.AuthorListCreateView.as_view(), name="author-list"),
    path("authors/<int:pk>/", views.AuthorDetailView.as_view(), name="author-detail"),
    path("books/", views.BookListCreateView.as_view(), name="book-list"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book-detail"),
    path("orders/", views.OrderListCreateView.as_view(), name="order-list"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("create-order/", views.create_order, name="create-order"),
    path("reviews/", views.ReviewListCreateView.as_view(), name="review-list"),
    path("reviews/<int:pk>/", views.ReviewDetailView.as_view(), name="review-detail"),
    path("export/", views.export_data, name="export"),
    path("schema/", schema_view.with_ui("swagger", cache_timeout=0), name="schema"),
    path(
        "schema/swagger-ui/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger-ui",
    ),
    path("schema/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
]
