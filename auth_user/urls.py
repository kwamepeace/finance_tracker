
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserAuthViewSet, PortfolioViewSet, HoldingsViewSet
from 

# Create a router to automatically handle URL patterns for viewsets.
router = DefaultRouter()
router.register(r'portfolio', PortfolioViewSet, basename='portfolio')
router.register(r'holdings', HoldingsViewSet, basename='holdings')

urlpatterns = [
    path('auth/register/', UserAuthViewSet.as_view({'post': 'register'}), name='register'),
    path('auth/login/', UserAuthViewSet.as_view({'post': 'login'}), name='login'),
    
    # Includes the default router URLs
    path('', include(router.urls)),
]
