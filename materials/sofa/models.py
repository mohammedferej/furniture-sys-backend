from django.db import models
from order.models import Order

class SofaMaterial(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sofa_materials')
    material_type= models.CharField(max_length=100)
    material_made_from= models.CharField(max_length=100)
    design_type = models.CharField(max_length=100)
    no_of_mekeda = models.IntegerField()
    no_of_pillow = models.IntegerField()
    uplift_or_height = models.CharField(max_length=20)
    room_size = models.IntegerField()
    room_shape = models.CharField(max_length=20)
    price_per_meter = models.DecimalField(max_digits=10, decimal_places=2)
   
    has_table=models.BooleanField(default=False)
    has_leg=models.BooleanField(default=False)

    def __str__(self):
        return f"Sofa for Order {self.order.order_code}"


class Segment(models.Model):
    material = models.ForeignKey(SofaMaterial, on_delete=models.CASCADE, related_name='segments')
    side_name = models.CharField(max_length=20)
    values = models.JSONField()

    def __str__(self):
        return f"Segment {self.side_name} for Sofa {self.material.id}"
