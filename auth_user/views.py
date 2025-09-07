from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import CustomUser, Portfolio, Holdings, Stock
from .serializers import PortfolioSerializer, HoldingsSerializer, LoginSerializer, UserSerializer


class UserAuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = LoginSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            #Token generated using signals.py 
            token = Token.objects.get(user=user)
            #Returns a token, user id and a success message upon successful registration
            return Response({
                'message': 'Account successfully created👌',
                'token': token.key, 
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id}, status=status.HTTP_200_OK)


class PortfolioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        # Restrict queryset to portfolios owned by the current user
        return Portfolio.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HoldingsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HoldingsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['stock__symbol', 'stock__name']
    ordering_fields = ['quantity', 'purchase_price', 'purchase_date']

    def get_queryset(self):
        # Restrict queryset to holdings within the user's portfolio
        return Holdings.objects.filter(portfolio__user=self.request.user)

    def perform_create(self, serializer):
        # Get the portfolio name and symbol from the request data
        portfolio_name = self.request.data.get('portfolio_name')
        stock_symbol = self.request.data.get('symbol')

        # Check for required fields
        if not portfolio_name:
            raise serializers.ValidationError({"portfolio_name": "This field is required."})
        if not stock_symbol:
            raise serializers.ValidationError({"symbol": "This field is required."})

        # Get the specific portfolio for the current user using the name
        try:
            user_portfolio = get_object_or_404(Portfolio, name=portfolio_name, user=self.request.user)
        except Exception:
            raise serializers.ValidationError({"portfolio_name": "Invalid portfolio name or you do not have permission to access this portfolio."})

        # Check if the stock already exists by its symbol or create a new one
        try:
            stock, created = Stock.objects.get_or_create(symbol=stock_symbol.upper(), defaults={'name': stock_symbol.upper()})
        except IntegrityError:
            raise serializers.ValidationError({"error": "This stock already exists in your portfolio."})
        
        # Removing the non-model fields from validated_data before saving
        validated_data = serializer.validated_data
        validated_data.pop('portfolio_name', None)
        validated_data.pop('symbol', None)
        
        # Save the serializer instance with the correct related objects
        serializer.save(portfolio=user_portfolio, stock=stock)
