from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager



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

    # Use the custom user manager for this model.
    objects = CustomUserManager()

    # Override the default username field to use email as the unique identifier.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def __str__(self):
        return self.email
    
 
    class Meta:
        # Custom permissions for the CustomUser model.
        permissions = (
            ("can_view_library", "Can view library"),
            ("can_manage_books", "Can manage books"),
        )


