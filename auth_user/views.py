from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db import IntegrityError
from .models import CustomUser, Portfolio, Holdings, Stock
from .serializers import PortfolioSerializer, HoldingsSerializer
from .forms import UserCreationForm


class UserAuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()

    @action(detail=False, methods=['post'])
    def register(self, request):
        form = UserCreationForm(request.data)
        if form.is_valid():
            user = form.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class PortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        This view should return a single portfolio for the currently authenticated user.
        """
        return Portfolio.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Creates a new portfolio for the authenticated user.
        A user can only have one portfolio.
        """
        if Portfolio.objects.filter(user=request.user).exists():
            return Response({'error': 'You can only have one portfolio.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='my-portfolio')
    def my_portfolio(self, request):
        portfolio = get_object_or_404(Portfolio, user=request.user)
        serializer = self.get_serializer(portfolio)
        return Response(serializer.data)


class HoldingsViewSet(viewsets.ModelViewSet):
    serializer_class = HoldingsSerializer
    permission_classes = [IsAuthenticated]
    queryset = Holdings.objects.all()

    def get_queryset(self):
        # Restrict queryset to holdings within the user's portfolio
        return Holdings.objects.filter(portfolio__user=self.request.user)

    def perform_create(self, serializer):
        user_portfolio = get_object_or_404(Portfolio, user=self.request.user)
        
        # Check if the stock already exists by its symbol or create a new one
        stock_symbol = self.request.data.get('symbol')
        if not stock_symbol:
            raise serializers.ValidationError({"symbol": "This field is required."})

        try:
            stock, created = Stock.objects.get_or_create(symbol=stock_symbol.upper(), defaults={'name': stock_symbol.upper()})
            serializer.save(portfolio=user_portfolio, stock=stock)
        except IntegrityError:
            raise serializers.ValidationError({"error": "This stock already exists in your portfolio."})
