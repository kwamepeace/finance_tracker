from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .forms import UserCreationForm, CustomUserChangeForm
from .models import CustomUser, Portfolio, Stock


class CustomUserAdmin(UserAdmin):
    """
    Custom admin for the CustomUser model.
    This allows us to add custom fields to the user creation and change forms.
    """
    add_form = UserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'email', 'date_of_birth', 'profile_photo', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_of_birth')
    fieldsets = [
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ( 'date_of_birth', 'profile_photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    ]

    """
     fields to be displayed when adding a new custom user. Overrides the default UserAdmin add_fieldsets
     to include custom fields.
     
    """
    add_fieldsets = [
        (None, 
        {   'classes': ['wide'],
            'fields': [ 'email', 'password1', 'password2', 'date_of_birth', 'profile_photo']
            }
        ),
    ]
    search_fields = ('email', 'username', 'date_of_birth')
    ordering = ['email',]   
    filter_horizontal = []

# Registering the CustomUser model with the custom admin
admin.site.register(CustomUser, CustomUserAdmin)


class PortfolioAdmin(admin.ModelAdmin):
    """
    Admin interface for the Portfolios model.
    """
    list_display = ('user', 'name')
    search_fields = ('name',)
    list_filter = ('user',)
admin.site.register(Portfolio, PortfolioAdmin)


class StockAdmin(admin.ModelAdmin):
    """
    Admin interface for the Stocks model.
    """
    list_display = ('name', 'symbol')
    search_fields = ('symbol',)
    list_filter = ('symbol',)
admin.site.register(Stock, StockAdmin)




