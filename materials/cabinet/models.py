from django.db import models
from order.models import Order

class BedMaterial(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='bed_materials')
    material_type= models.CharField(max_length=100)
    material_made_from= models.CharField(max_length=100)
    design_type = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    height = models.IntegerField()
    side_length = models.CharField(max_length=20)
    inner_width = models.CharField(max_length=20)
    no_of_care=models.IntegerField()
    price_per_care=models.DecimalField(max_digits=10, decimal_places=2)
   
    def __str__(self):
        return f"cabinet for Order {self.order.order_code}"

