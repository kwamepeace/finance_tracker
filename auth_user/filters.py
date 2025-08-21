from django_filters import filters
from .models import Stocks, Portfolios


class StocksFilter(filters.FilterSet):
    class Meta:
        model = Stocks
        fields = {
            'name': ['exact', 'icontains'],
            'author__name': ['exact', 'icontains'],
            'published_date': ['exact', 'year__gt', 'year__lt'],
        }