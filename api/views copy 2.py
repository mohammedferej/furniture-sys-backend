from materials.mejlis.models import MejlisMaterial, Segment
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from datetime import datetime
from customer.models import Customer
from order.models import Order
from order.utils import generate_order_pdf

from django.db import transaction

from decimal import Decimal

class CreateOrderView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        print("==inside the post")

        try:
            with transaction.atomic():  # Ensure all-or-nothing
                # 1. Create or update customer
                customer_data = data.get('customer', {})
                customer, created = Customer.objects.get_or_create(
                    phone=customer_data.get('phone'),
                    defaults={
                        'name': customer_data.get('name'),
                        'address': customer_data.get('address')
                    }
                )
                if not created:
                    customer.name = customer_data.get('name', customer.name)
                    customer.address = customer_data.get('address', customer.address)
                    customer.save()

                # 2. Create order
                order_data = data.get('order', {})
                receive_date = datetime.fromisoformat(
                    order_data['receive_order_at'].replace('Z', '+00:00')
                )
                completed_date = (
                    datetime.fromisoformat(order_data['completed_order_at'].replace('Z', '+00:00'))
                    if order_data['completed_order_at'] else None
                )

                order = Order.objects.create(
                    customer=customer,
                    order_code=order_data.get('order_code'),
                    receive_order_at=receive_date.date(),
                    completed_order_at=completed_date.date() if completed_date else None,
                    total_price=Decimal(order_data.get('total_price', '0')),
                    remaining_payment=Decimal(order_data.get('remaining_payment', '0')),
                    app_front=Decimal(order_data.get('app_front', '0'))
                )

                # 3. Create MejlisMaterial linked to order
                material_data = order_data.get('material_details', {})
                material = MejlisMaterial.objects.create(
                    order=order,
                    material_type=order_data.get('material_type'),
                    material_made_from=material_data.get('material_made_from'),
                    design_type=material_data.get('design_type'),
                    no_of_mekeda=material_data.get('no_of_mekeda'),
                    no_of_pillow=material_data.get('no_of_pillow'),
                    uplift_or_height=material_data.get('uplift_or_height'),
                    room_size=material_data.get('room_size'),
                    room_shape=material_data.get('room_shape'),
                    price_per_meter=material_data.get('price_per_meter'),
                    has_table=material_data.get('has_table', False)
                )

                # 4. Create segments linked to material
                for side_name, values in material_data.get('segments', {}).items():
                    Segment.objects.create(
                        material=material,
                        side_name=side_name,
                        values=values
                    )

                # 5. Generate PDF
                try:
                    pdf_url = generate_order_pdf(order)
                    return Response({
                        "message": "Order created successfully",
                        "pdf_url": request.build_absolute_uri(pdf_url),
                        "order_id": order.id
                    }, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({
                        "message": "Order created but PDF generation failed",
                        "error": str(e),
                        "order_id": order.id
                    }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# api/views.py
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from order.models import Order
from .serializers import OrderSerializer

class StandardPagination(PageNumberPagination):
    print("= inside orderlist =")
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

class OrderList(generics.ListAPIView):
    print("= inside orderlist =")
    queryset = Order.objects.select_related('customer').all()
    serializer_class = OrderSerializer
    pagination_class = StandardPagination



from rest_framework import generics
from order.models import Order
from .serializers import OrderSerializer

# class OrderList(generics.ListCreateAPIView):
#     print("OrderList class ***...")
#     queryset = Order.objects.select_related('customer').prefetch_related('mejlis_materials', 'mejlis_materials__segments').all()
#     serializer_class = OrderSerializer

class OrderDetail(generics.RetrieveUpdateAPIView):
    print("OrderDetail class ...")
    queryset = Order.objects.select_related('customer').prefetch_related('mejlis_materials', 'mejlis_materials__segments').all()
    serializer_class = OrderSerializer


def perform_update(self, serializer):
    order = serializer.save()

    # --- Update customer ---
    customer_data = self.request.data.get('customer', {})
    if customer_data:
        # Check if phone already belongs to a different customer
        new_phone = customer_data.get('phone')
        if new_phone and order.customer.phone != new_phone:
            if Customer.objects.filter(phone=new_phone).exclude(id=order.customer.id).exists():
                raise ValidationError({"customer": {"phone": ["Customer with this phone already exists."]}})
            order.customer.phone = new_phone
        
        order.customer.name = customer_data.get('name', order.customer.name)
        order.customer.address = customer_data.get('address', order.customer.address)
        order.customer.save()

    # --- Update materials ---
    materials_data = self.request.data.get('mejlis_materials', [])
    if materials_data:
        # Delete old materials & segments
        order.mejlis_materials.all().delete()

        for material_data in materials_data:
            segments_data = material_data.pop('segments', [])
            material = MejlisMaterial.objects.create(order=order, **material_data)

            for seg in segments_data:
                Segment.objects.create(material=material, **seg)

    # --- Optional: return order ---
    return order
