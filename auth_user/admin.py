from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .forms import UserCreationForm, CustomUserChangeForm
from .models import CustomUser


# Register your models here.


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

# Register the CustomUser model with the custom admin
admin.site.register(CustomUser, CustomUserAdmin)

# Unregister the default Group model to avoid conflicts
# Optional, but if you don't need the Group model, you can unregister it
#

