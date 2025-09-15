from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


def generate_user_id():
    return str(uuid.uuid4())


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
        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractUser):
    id = models.CharField(
        max_length=36, primary_key=True, default=generate_user_id, editable=False
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        permissions = [
           

 ("can_add_mejlis", "Can add a Mejlis"),
            ("can_edit_mejlis", "Can edit a Mejlis"),
            ("can_delete_mejlis", "Can delete a Mejlis"),
            ("can_view_mejlis", "Can view a Mejlis"),

            # Bed
            ("can_add_bed", "Can add a Bed"),
            ("can_edit_bed", "Can edit a Bed"),
            ("can_delete_bed", "Can delete a Bed"),
            ("can_view_bed", "Can view a Bed"),

            # TV Stand
            ("can_add_tvstand", "Can add a TV Stand"),
            ("can_edit_tvstand", "Can edit a TV Stand"),
            ("can_delete_tvstand", "Can delete a TV Stand"),
            ("can_view_tvstand", "Can view a TV Stand"),

            # Kitchen Cabinet
            ("can_add_kitchen_cabinet", "Can add a Kitchen Cabinet"),
            ("can_edit_kitchen_cabinet", "Can edit a Kitchen Cabinet"),
            ("can_delete_kitchen_cabinet", "Can delete a Kitchen Cabinet"),
            ("can_view_kitchen_cabinet", "Can view a Kitchen Cabinet"),

            # Sofa
            ("can_add_sofa", "Can add a Sofa"),
            ("can_edit_sofa", "Can edit a Sofa"),
            ("can_delete_sofa", "Can delete a Sofa"),
            ("can_view_sofa", "Can view a Sofa"),


          

            # ----- Orders -----
            ("can_create_order", "Can create an order"),
            ("can_update_order", "Can update an order"),
            ("can_cancel_order", "Can cancel an order"),
            ("can_view_order", "Can view orders"),

            # ----- User & Role Management -----
            ("can_create_user", "Can create a user"),
            ("can_edit_user", "Can edit a user"),
            ("can_delete_user", "Can delete a user"),
            ("can_view_user", "Can view users"),
            ("can_block_user", "Can block a user"),
            ("can_reset_password", "Can reset another user's password"),


            # ----- System/Group Permissions -----
            ("can_create_group", "Can create a group"),
            ("can_update_group", "Can update a group"),
            ("can_assign_group", "Can assign a group to a user"),
            ("can_remove_group", "Can remove a group from a user"),

            ("can_assign_permission", "Can assign a permission to a group"),
            ("can_remove_permission", "Can remove a permission from a group"),

            

        
        ]

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"
