from django.contrib.auth.models import AbstractUser, BaseUserManager,Permission
from django.db import models
import uuid

def generate_user_id():
    return str(uuid.uuid4())
def generate_role_id():
    return str(uuid.uuid4())

# ROLE_CHOICES = [
#     ('admin', 'Admin'),
#     ('manager', 'Manager'),
#     ('staff', 'Staff'),
#     ('customer', 'Customer'),
# ]

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(username, password, **extra_fields)

class Role(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=generate_role_id, editable=False)
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.name
class CustomUser(AbstractUser):
    id = models.CharField(max_length=36, primary_key=True, default=generate_user_id, editable=False)
    #role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    role = models.ForeignKey(Role,null=True, blank=True, on_delete=models.SET_NULL,related_name='users')
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        # Custom permissions in addition to default Django permissions
        permissions = [
            ("can_assign_role", "Can assign a role to another user"),
            ("can_block_user", "Can block a user"),
            ("can_reset_password", "Can reset another user's password"),
        ]

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


