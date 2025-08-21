from rest_framework import serializers
from .models import Portfolios, Stocks


class PortfoliosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolios
        fields = ['__all__']

class StocksSerializer(serializers.ModelSerializer):
    total_amount = serializers.SerializerMethodField()
    class Meta:
        model = Stocks
        fields = ['portfolio', 'symbol', 'units', 'purchase_price', 'purchase_date']


        def get_total_amount(self, obj):
            return obj.units * obj.purchase_date
        
        def validate(self, data):
            if not isinstance(data['units'], int) or not isinstance(data['purchase_price'], int):
                raise serializers.ValidationError("Units and purchase price must be integers.")

        
        



    



