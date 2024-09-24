from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    """
    Custom user manager that uses email as the unique identifier for authentication
    instead of usernames.
    """

    def create_user(self, username, password=None, **extra_fields):
        """
        Create and save a user with the given username and password.
        """
        
        if not username:
            raise ValueError('The username field must be set')
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Create and save a superuser with the given username and password.
        """
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractUser):
    # currently Discovered Check doesn't collect or use email, but it's here for future use
    email = models.EmailField(unique=True, blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects: CustomUserManager = CustomUserManager() 

    def __str__(self):
        return self.username


class AuthToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    token_acquired_at = models.DateTimeField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.user.email}\'s token'
