from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings


class CustomUserManager(BaseUserManager):
    """
    Custom manager for the CustomUser model.
    """
    def create_user(self, username, email, password=None, **extra_fields): 
        """
        Creates and returns a user with an email, username, and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        # Creates and returns a superuser with an email, username, and password.
        user = self.create_user(username, email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user 
        

class CustomUser(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    Adds date_of_birth and profile_photo fields.
    """
    date_of_birth = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=150, unique=True)

    # Using the custom user manager for this model.
    objects = CustomUserManager()

    # Overriding the default username field to use email for logging in.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def __str__(self):
        return self.email
    
 
    class Meta:
        # Custom permissions for the CustomUser model.
        permissions = [
            ('can_view_portfolios', 'Can view portfolios'),
            ('can_manage_portfolios', 'Can manage portfolios'),
        ]
           


'''
Stock Model to represent individual stocks.
This model includes fields for the stock name, symbol, and purchase date.

'''
class Stock(models.Model):
    class Meta:
        verbose_name = 'Stock'
        permissions = [
            ("can_view_stocks", "Can view stocks"),
            ("can_manage_stocks", "Can manage stocks"),
        ]
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.symbol

'''
 Holdings (Through) Model, an intermediary table for the many-to-many relationship between Portfolios and Stocks.
 This model tracks the quantity of each stock in a portfolio and the purchase price.
 
 '''
class Holdings(models.Model):
    class Meta:
        verbose_name = 'Holding'
        permissions = [
            ("can_view_holdings", "Can view holdings"),
            ("can_manage_holdings", "Can manage holdings"),
        ]
    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=4)
    purchase_date = models.DateField(auto_now_add=True)
    
    class Meta:
        # Ensures that each portfolio-stock combination is unique
        unique_together = ('portfolio', 'stock')

    def __str__(self):
        return f"{self.quantity} of {self.stock.symbol} in {self.portfolio.name}"

class Portfolio(models.Model):
    class Meta:
        verbose_name = 'Portfolio'
        permissions = [
            ("can_view_portfolios", "Can view portfolios"),
            ("can_manage_portfolios", "Can manage portfolios"),
        ]
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    stocks = models.ManyToManyField(Stock, through='Holdings', related_name='portfolios_stocks')
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"