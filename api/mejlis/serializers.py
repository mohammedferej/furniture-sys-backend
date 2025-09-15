# api/mejlis/serializers.py
import logging
from rest_framework import serializers
from order.models import Order
from customer.models import Customer
from materials.mejlis.models import MejlisMaterial, Segment

logger = logging.getLogger("orders")


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = ['side_name', 'values']


class MejlisMaterialSerializer(serializers.ModelSerializer):
    segments = SegmentSerializer(many=True, read_only=True)

    class Meta:
        model = MejlisMaterial
        fields = [
            
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


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address']


class OrderReadSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    mejlis_materials = MejlisMaterialSerializer(many=True, read_only=True)

    order = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'mejlis_materials',
            
            'order'
        ]

    def get_order(self, obj):
        return {
            'material_type':obj.material_type,
            "document_path": obj.document_path.url if obj.document_path else None,
            "total_price": str(obj.total_price),
            "app_front": str(obj.app_front),
            "remaining_payment": str(obj.remaining_payment),
            "status": obj.status,
            "receive_order_at": obj.receive_order_at,
            "completed_order_at": obj.completed_order_at,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }



class SegmentWriteSerializer(serializers.Serializer):
    side_name = serializers.CharField()
    values = serializers.ListField(child=serializers.IntegerField())


class MejlisMaterialWriteSerializer(serializers.Serializer):
    material_type = serializers.CharField()
    material_made_from = serializers.CharField()
    design_type = serializers.CharField()
    no_of_mekeda = serializers.IntegerField()
    no_of_pillow = serializers.IntegerField()
    uplift_or_height = serializers.CharField()
    room_size = serializers.IntegerField()
    room_shape = serializers.CharField()
    price_per_meter = serializers.DecimalField(max_digits=12, decimal_places=2)
    has_table = serializers.BooleanField(default=False)
    segments = SegmentWriteSerializer(many=True, required=False)


class OrderWriteSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    order = serializers.DictField(write_only=True)

    class Meta:
        model = Order
        fields = ['customer', 'order']

    def create(self, validated_data):
        logger.info("Creating order from nested structure")
        customer_data = validated_data.pop("customer")
        order_data = validated_data.pop("order")

        # --- Handle customer ---
        customer, created = Customer.objects.get_or_create(
            phone=customer_data["phone"], defaults=customer_data
        )
        if not created:
            for attr, value in customer_data.items():
                setattr(customer, attr, value)
            customer.save()

        # --- Create order ---
        material_type = order_data["material_type"]
        material_details = order_data.pop("material_details", {})

        order = Order.objects.create(
            customer=customer,
            **order_data
        )

        # --- Create MejlisMaterial ---
        if material_type:
            segments = material_details.pop("segments", {})
            material = MejlisMaterial.objects.create(
                order=order,
                #material_type=material_type,
                **material_details
            )

            
        if isinstance(segments, dict):
            segments = [{"side_name": k, "values": v} for k, v in segments.items()]

        for seg in segments:
            Segment.objects.create(
                material=material,
                side_name=seg['side_name'],
                values=seg['values']
            )


        return order

    def update(self, instance, validated_data):
        # --- Update customer ---
        customer_data = validated_data.pop("customer", None)
        if customer_data:
            customer = instance.customer
            for attr, value in customer_data.items():
                setattr(customer, attr, value)
            customer.save()

        # --- Update order fields ---
        order_data = validated_data.pop("order", None)
        if order_data:
            for attr, value in order_data.items():
                setattr(instance, attr, value)
            instance.save()

        # --- Update mejlis_materials ---
        materials_data = validated_data.pop("mejlis_materials", None)
        if materials_data:
            for material_data in materials_data:
                segments_data = material_data.pop("segments", {})
                material_type = material_data.pop("material_type", None)

                # Check if material exists for this order and type
                material, created = MejlisMaterial.objects.get_or_create(
                    order=instance,
                    material_type=material_type,
                    defaults=material_data
                )
                if not created:
                    for attr, value in material_data.items():
                        setattr(material, attr, value)
                    material.save()

                # Update segments
                if segments_data:
                    material.segments.all().delete()  # remove old segments
                    for side_name, values in segments_data.items():
                        Segment.objects.create(
                            material=material,
                            side_name=side_name,
                            values=values
                        )

        return instance
