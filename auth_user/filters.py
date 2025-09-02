from django_filters import filters
from .models import Stock, Holdings


class StocksFilter(filters.FilterSet):
    class Meta:
        model = Stock
        fields = {
            'name': ['exact', 'icontains'],
            'symbol': ['exact', 'icontains'],
        }

    
class HoldingsFilter(filters.FilterSet):
    class Meta:
        model = Holdings
        fields = {
            'portfolio__name': ['exact', 'icontains'],
            'quantity': ['exact', 'gte', 'lte'],
            'purchase_price': ['exact', 'gte', 'lte'],
            'purchase_date': ['exact', 'gte', 'lte'],
        }