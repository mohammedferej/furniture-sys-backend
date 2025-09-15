# api/serializers.py
from rest_framework import serializers
from order.models import Order
from customer.models import Customer
from materials.mejlis.models import MejlisMaterial, Segment

class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = ['side_name', 'values']

class MejlisMaterialSerializer(serializers.ModelSerializer):
    segments = SegmentSerializer(many=True)

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

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address']

class OrderSerializer(serializers.ModelSerializer):
    print("***order detail***")
    customer = CustomerSerializer()
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
        customer_data = validated_data.pop('customer')
        materials_data = validated_data.pop('mejlis_materials', [])

        # Create or get customer
        customer, created = Customer.objects.get_or_create(
            phone=customer_data['phone'],
            defaults=customer_data
        )
        if not created:
            for attr, value in customer_data.items():
                setattr(customer, attr, value)
            customer.save()

        order = Order.objects.create(customer=customer, **validated_data)

        for material_data in materials_data:
            segments_data = material_data.pop('segments', [])
            material = MejlisMaterial.objects.create(order=order, **material_data)

            for segment_data in segments_data:
                Segment.objects.create(material=material, **segment_data)

        return order

    def update(self, instance, validated_data):
        print("this is the place")
        customer_data = validated_data.pop('customer', None)
        materials_data = validated_data.pop('mejlis_materials', None)

        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update customer
        if customer_data:
            customer = instance.customer
            for attr, value in customer_data.items():
                setattr(customer, attr, value)
            customer.save()

        # Update mejlis_materials and segments
        if materials_data is not None:
            # Delete old materials & segments
            instance.mejlis_materials.all().delete()
            for material_data in materials_data:
                segments_data = material_data.pop('segments', [])
                material = MejlisMaterial.objects.create(order=instance, **material_data)
                for segment_data in segments_data:
                    Segment.objects.create(material=material, **segment_data)

        return instance
