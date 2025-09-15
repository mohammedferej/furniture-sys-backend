# api/mejlis/views.py
import logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .serializers import OrderReadSerializer, OrderWriteSerializer
from order.models import Order
from order.utils import generate_order_pdf

logger = logging.getLogger("orders")


# Create Order
class CreateOrderView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderWriteSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    order = serializer.save()
                    pdf_url = generate_order_pdf(order)
                    return Response({
                        "message": "Order created successfully",
                        "order_id": order.id,
                        "pdf_url": request.build_absolute_uri(pdf_url)
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.exception("Error creating order")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# List Orders
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by("-id")
    serializer_class = OrderReadSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "status": ["exact"],
        "created_at": ["gte", "lte"],
        "customer__name": ["icontains"],
    }
    search_fields = ["customer__name", "customer__phone"]
    ordering_fields = ["id", "created_at", "total_price"]


# Retrieve single order
class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderReadSerializer
    lookup_field = "id"


# # Update order
# class OrderUpdateView(APIView):
#     def put(self, request, id, *args, **kwargs):
#         order = get_object_or_404(Order, id=id)
#         serializer = OrderWriteSerializer(order, data=request.data, partial=True)
#         if serializer.is_valid():
#             try:
#                 with transaction.atomic():
#                     order = serializer.save()
#                     pdf_url = generate_order_pdf(order)
#                     return Response({
#                         "message": "Order updated successfully",
#                         "order_id": order.id,
#                         "pdf_url": request.build_absolute_uri(pdf_url)
#                     })
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class OrderUpdateView(APIView):
    def put(self, request, id, *args, **kwargs):
        order = get_object_or_404(Order, id=id)
        serializer = OrderWriteSerializer(order, data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    order = serializer.save()

                    # --- Generate PDF with updated values ---
                    try:
                        pdf_url = generate_order_pdf(order)
                    except Exception as e:
                        logger.error(f"PDF generation failed: {e}")
                        pdf_url = None

                    return Response({
                        "message": "Order updated successfully",
                        "order_id": order.id,
                        "pdf_url": request.build_absolute_uri(pdf_url) if pdf_url else None
                    }, status=200)

            except Exception as e:
                logger.exception("Error while updating order")
                return Response({"error": str(e)}, status=400)

        return Response(serializer.errors, status=400)


# Delete order
class OrderDeleteView(APIView):
    def delete(self, request, id, *args, **kwargs):
        order = get_object_or_404(Order, id=id)
        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Update only status
class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderReadSerializer
    lookup_field = "id"

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get("status")
        valid_statuses = dict(Order.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Valid options are: {list(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = new_status
        order.save(update_fields=["status"])
        return Response({"message": f"Order {order.id} status updated to {order.status}"})
class OrderByMaterialTypeView(generics.ListAPIView):
    serializer_class = OrderReadSerializer

    def get_queryset(self):
        material_type = self.kwargs["material_type"]  # get from URL
        return Order.objects.filter(material_type=material_type)
class OrderByStatusView(generics.ListAPIView):
    serializer_class = OrderReadSerializer

    def get_queryset(self):
        status = self.kwargs["status"]  # get from URL
        return Order.objects.filter(status=status)

