import django_filters
from django_filters import RangeFilter

from .models import Book


class BookFilter(django_filters.FilterSet):
    """Фильтр для книг с поддержкой диапазона цен"""

    price = RangeFilter(field_name="price", lookup_expr="range")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Book
        fields = ["author", "price", "price_min", "price_max"]