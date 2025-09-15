import logging
from rest_framework import serializers
from order.models import Order
from customer.models import Customer
from materials.mejlis.models import MejlisMaterial, Segment

logger = logging.getLogger("orders")


class SegmentSerializer(serializers.Serializer):
    # Instead of ModelSerializer, use Serializer for dict input
    side_name = serializers.CharField()
    values = serializers.ListField(child=serializers.IntegerField())

class MejlisMaterialSerializer(serializers.ModelSerializer):
    # for read: convert Segment instances to dict
    segments = serializers.SerializerMethodField()

    class Meta:
        model = MejlisMaterial
        fields = [
            'material_type',
            'material_made_from',
            'design_type',
            'no_of_mekeda',
            'no_of_pillow',
            'uplift_or_height',
            'room_size',
            'room_shape',
            'price_per_meter',
            'has_table',
            'segments'
        ]

    def get_segments(self, obj):
        # obj.segments is a RelatedManager
        return {seg.side_name: seg.values for seg in obj.segments.all()}


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address']

    def validate_phone(self, value):
        # Only check uniqueness for other customers, ignore self
        if self.instance:
            if Customer.objects.exclude(id=self.instance.id).filter(phone=value).exists():
                raise serializers.ValidationError("This phone is already taken by another customer.")
        else:
            # On create, check uniqueness normally
            if Customer.objects.filter(phone=value).exists():
                raise serializers.ValidationError("This phone is already taken.")
        return value



class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.DictField()
    mejlis_materials = MejlisMaterialSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_code',
            'customer',
            'receive_order_at',
            'completed_order_at',
            'total_price',
            'remaining_payment',
            'app_front',
            'document_path',
            'mejlis_materials'
        ]

    def create(self, validated_data):
        logger.info("Creating order (serializer.create)")
        customer_data = validated_data.pop("customer")
        materials_data = validated_data.pop("mejlis_materials", [])

        customer, created = Customer.objects.get_or_create(
            phone=customer_data["phone"], defaults=customer_data
        )
        if not created:
            for attr, value in customer_data.items():
                setattr(customer, attr, value)
            customer.save()

        order = Order.objects.create(customer=customer, **validated_data)

        for material_data in materials_data:
            segments = material_data.pop("segments", {})
            material = MejlisMaterial.objects.create(order=order, **material_data)

            if isinstance(segments, dict):
                for side_name, values in segments.items():
                    Segment.objects.create(
                        material=material, side_name=side_name, values=values
                    )

        return order

    
    def update(self, instance, validated_data):
        customer_data = validated_data.pop("customer", None)
        materials_data = validated_data.pop("mejlis_materials", None)

        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update customer manually
        if customer_data:
            customer = instance.customer
            new_phone = customer_data.get("phone")

            if new_phone and new_phone != customer.phone:
                # Only fail if another customer already has this phone
                if Customer.objects.exclude(id=customer.id).filter(phone=new_phone).exists():
                    raise serializers.ValidationError(
                        {"customer": {"phone": ["This phone is already taken."]}}
                    )

            for attr, value in customer_data.items():
                setattr(customer, attr, value)
            customer.save()

        # Update materials as before...
        # <keep your existing mejlis_materials update code>

        return instance
