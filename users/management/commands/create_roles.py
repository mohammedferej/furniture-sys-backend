# users/management/commands/create_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from order.models import Order

class Command(BaseCommand):
    help = "Create default roles and permissions"

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        staff_group, _ = Group.objects.get_or_create(name="Staff")
        customer_group, _ = Group.objects.get_or_create(name="Customer")

        # Example: assign permissions
        order_ct = ContentType.objects.get_for_model(Order)

        # Admin can do everything
        all_perms = Permission.objects.filter(content_type=order_ct)
        admin_group.permissions.set(all_perms)

        # Manager: can view & change orders
        view_order = Permission.objects.get(codename="view_order", content_type=order_ct)
        change_order = Permission.objects.get(codename="change_order", content_type=order_ct)
        manager_group.permissions.set([view_order, change_order])

        # Staff: only view
        staff_group.permissions.set([view_order])

        # Customer: only view their own orders (we enforce this in views)
        customer_group.permissions.set([])

        self.stdout.write(self.style.SUCCESS("Roles and permissions created."))
