from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Portfolio, Stock, Holdings
from .services import get_live_stock_price


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        user = authenticate(email=data.get('email'), password=data.get('password'))
        if user:
            # Check if the user is active
            if user.is_active:
                # Store the user object in validated_data
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError("User account is inactive.")
        else:
            raise serializers.ValidationError("Invalid credentials.")


"""
HoldingsSerializer: Serializes the Holdings model, including fields for id, symbol, quantity, purchase_price, purchase_date, and total_amount.
It also includes a method to calculate the total amount (quantity * purchase_price) and validation to ensure quantity and purchase_price are positive.
"""
class HoldingsSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source='stock.symbol', read_only=True)
    total_amount = serializers.SerializerMethodField()
    current_price = serializers.SerializerMethodField()
    current_value = serializers.SerializerMethodField()

    class Meta:
        model = Holdings
        fields = ['id', 'symbol', 'quantity', 'purchase_price', 'purchase_date', 'total_amount', 'current_price', 'current_value']
        read_only_fields = ['purchase_date']

    def get_total_amount(self, obj):
        return obj.quantity * obj.purchase_price
    
    def get_current_price(self, obj):
        # Fetch the live price for the stock
        return get_live_stock_price(obj.stock.symbol)

    def get_current_value(self, obj):
        # Calculate the current value based on the live price
        live_price = self.get_current_price(obj)
        if live_price is not None:
            return obj.quantity * live_price
        return None
    
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
        # Gracefully handle cases where the API call returns None
        total_value = sum(
            holding.quantity * price if (price := get_live_stock_price(holding.stock.symbol)) is not None else 0
            for holding in obj.holdings_set.all()
        )
        return total_value
