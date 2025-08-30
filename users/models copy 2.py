# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid

def generate_user_id():
    return str(uuid.uuid4())

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.must_change_password = True
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractUser):
    id = models.CharField(max_length=36, primary_key=True, default=generate_user_id, editable=False)
    email = models.EmailField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500, null=True)
    is_newsletter_subscribed = models.BooleanField(default=False)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Add 'email' if needed

    def __str__(self):
        return f'{self.username} ({self.first_name} {self.last_name})'
