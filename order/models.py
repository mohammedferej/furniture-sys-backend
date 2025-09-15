from django.db import models
from customer.models import Customer


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    MATERIAL_CHOICES = [
        ("mejlis", "Mejlis"),
        ("sofa", "Sofa"),
        ("bed", "Bed"),
        ("kitchen_cabinet", "Kitchen Cabinet"),
        ("cupboard", "Cupboard"),
        ("tvstand", "TV Stand"),
    ]
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    order_code = models.CharField(max_length=50, unique=True)
    material_type = models.CharField(max_length=50, choices=MATERIAL_CHOICES ,null=True,
    blank=True)

    receive_order_at = models.DateField()
    completed_order_at = models.DateField(null=True, blank=True)

    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    app_front = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # Advance payment
    app_front_received_date = models.DateField(null=True, blank=True)
    remaining_payment = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )

    document_path = models.FileField(
        upload_to="order_documents/", null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)  # auto timestamp
    updated_at = models.DateTimeField(auto_now=True)  # auto timestamp

    def save(self, *args, **kwargs):
        # Automatically update remaining_payment
        if self.total_price is not None and self.app_front is not None:
            self.remaining_payment = self.total_price - self.app_front
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_code} - {self.customer.name}"
