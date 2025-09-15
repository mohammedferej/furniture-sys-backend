from django.db import models
from customer.models import Customer

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_code = models.CharField(max_length=50, unique=True)
    receive_order_at = models.DateField()
    completed_order_at = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_payment = models.DecimalField(max_digits=10, decimal_places=2)
    app_front = models.DecimalField(max_digits=10, default=0 ,decimal_places=2)
    app_front_received_date=models.DateField(null=True, blank=True)
   
    document_path = models.FileField(upload_to='order_documents/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.order_code} - {self.customer.name}"
