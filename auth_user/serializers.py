from rest_framework import serializers
from .models import Portfolio, Stock, Holdings


"""
HoldingsSerializer: Serializes the Holdings model, including fields for id, symbol, quantity, purchase_price, purchase_date, and total_amount.
It also includes a method to calculate the total amount (quantity * purchase_price) and validation to ensure quantity and purchase_price are positive.
"""
class HoldingsSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source='stock.symbol', read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Holdings
        fields = ['id', 'symbol', 'quantity', 'purchase_price', 'purchase_date', 'total_amount']
        read_only_fields = ['purchase_date']

    def get_total_amount(self, obj):
        return obj.quantity * obj.purchase_price
    
        # using a object- level validation to validate quantity and purchase_price
    def validate(self, data):
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        if data['purchase_price'] <= 0:
            raise serializers.ValidationError("Purchase price must be a positive number.")
        return data
    


class PortfolioSerializer(serializers.ModelSerializer):
    stocks = HoldingsSerializer(source='holdings_set', many=True, read_only=True)
    total_portfolio_value = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'user', 'stocks', 'total_portfolio_value']
        read_only_fields = ['user']

    def get_total_portfolio_value(self, obj):
        total_value = sum(holding.quantity * holding.purchase_price for holding in obj.holdings_set.all())
        return total_value

# class StocksSerializer(serializers.ModelSerializer):
#     total_amount = serializers.SerializerMethodField()
#     class Meta:
#         model = Stock
#         fields = ['portfolio', 'symbol', 'units', 'purchase_price', 'purchase_date']


#         def get_total_amount(self, obj):
#             return obj.units * obj.quantity
        
#         def validate(self, data):
#             if not isinstance(data['units'], int) or not isinstance(data['purchase_price'], int):
#                 raise serializers.ValidationError("Units and purchase price must be integers.")

        
        



    



