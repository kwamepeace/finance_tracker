from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Portfolio, Stock, Holdings, CustomUser


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user registration and creation and 
    includes an additional password2 field to confirm password.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'date_of_birth', 'profile_photo']
    
    def validate(self, data):
        """
        Custom validation to ensure both password fields match.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """
        Creates and saves a new user with the validated data, securely hashing the password.
        """
        # Exclude password2 from the validated_data before creating the user
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            date_of_birth=validated_data.get('date_of_birth'),
            profile_photo=validated_data.get('profile_photo')
        )
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        user = authenticate(email=data.get('email'), password=data.get('password'))
        if user:
            if user.is_active:
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError("User account is inactive.")
        else:
            raise serializers.ValidationError("Invalid password or email.")


class HoldingsSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source='stock.symbol', read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Holdings
        fields = ['id', 'symbol', 'quantity', 'purchase_price', 'purchase_date', 'total_amount']
        read_only_fields = ['purchase_date']

    def get_total_amount(self, obj):
        return obj.quantity * obj.purchase_price
    
    def validate(self, data):
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        if data['purchase_price'] <= 0:
            raise serializers.ValidationError("Purchase price must be a positive number.")
        return data


class PortfolioSerializer(serializers.ModelSerializer):
    stocks = HoldingsSerializer(source='holdings_set', many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'user', 'stocks']
        read_only_fields = ['user']
