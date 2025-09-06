from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
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
            return Response({'token': token.key, 'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id}, status=status.HTTP_200_OK)


class PortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure a user can only see their own portfolio
        return Portfolio.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='my-portfolio')
    def my_portfolio(self, request):
        #  Will now return a list if a user has multiple portfolios
        portfolios = Portfolio.objects.filter(user=request.user)
        serializer = self.get_serializer(portfolios, many=True)
        return Response(serializer.data)


class HoldingsViewSet(viewsets.ModelViewSet):
    serializer_class = HoldingsSerializer
    permission_classes = [IsAuthenticated]
    queryset = Holdings.objects.all()
    
    # Add search and ordering functionality
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['stock__symbol', 'stock__name']
    ordering_fields = ['quantity', 'purchase_price', 'purchase_date']

    def get_queryset(self):
        # Restrict queryset to holdings within the user's portfolio
        return Holdings.objects.filter(portfolio__user=self.request.user)

    def perform_create(self, serializer):
        #  Get the portfolio ID from the request data
        portfolio_id = self.request.data.get('portfolio_id')
        if not portfolio_id:
            raise serializers.ValidationError({"portfolio_id": "This field is required."})

        #  Get the specific portfolio for the current user
        try:
            user_portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=self.request.user)
        except Exception:
            raise serializers.ValidationError({"portfolio_id": "Invalid portfolio ID or you do not have permission to access this portfolio."})

        # Check if the stock already exists by its symbol or create a new one
        stock_symbol = self.request.data.get('symbol')
        if not stock_symbol:
            raise serializers.ValidationError({"symbol": "This field is required."})

        try:
            stock, created = Stock.objects.get_or_create(symbol=stock_symbol.upper(), defaults={'name': stock_symbol.upper()})
            serializer.save(portfolio=user_portfolio, stock=stock)
        except IntegrityError:
            raise serializers.ValidationError({"error": "This stock already exists in your portfolio 😎."})
