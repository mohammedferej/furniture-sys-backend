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
    segments = SegmentSerializer(many=True, required=False)

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

    def to_internal_value(self, data):
        # If segments is dict {"side1": [...], "side2": [...]} → convert to list
        segments = data.get('segments')
        if isinstance(segments, dict):
            data['segments'] = [{'side_name': k, 'values': v} for k, v in segments.items()]
        return super().to_internal_value(data)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address']


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    order = serializers.DictField(write_only=True)  # nested order dict
    mejlis_materials = MejlisMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'order',              # input
            'mejlis_materials',   # output
            'document_path'
        ]

    def create(self, validated_data):
        logger.info("Creating order from nested Postman structure")

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
        material_type = order_data.pop("material_type", None)
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
                material_type=material_type,
                **material_details
            )

            # --- Create Segments ---
            for side_name, values in segments.items():
                Segment.objects.create(
                    material=material,
                    side_name=side_name,
                    values=values
                )

        return order
