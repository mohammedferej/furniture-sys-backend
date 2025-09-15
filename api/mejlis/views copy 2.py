import logging
from rest_framework import status, generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from .serializers import OrderSerializer
from order.models import Order
from order.utils import generate_order_pdf

logger = logging.getLogger("orders")


# ✅ Create Order
class CreateOrderView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info("POST /orders - Create order request received")
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    order = serializer.save()
                    try:
                        pdf_url = generate_order_pdf(order)
                        return Response({
                            "message": "Order created successfully",
                            "order_id": order.id,
                            "pdf_url": request.build_absolute_uri(pdf_url)
                        }, status=status.HTTP_201_CREATED)
                    except Exception as e:
                        logger.error(f"PDF generation failed: {e}")
                        return Response({
                            "message": "Order created but PDF generation failed",
                            "order_id": order.id,
                            "error": str(e)
                        }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.exception("Error while creating order")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        logger.warning(f"Validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ List all orders with filters
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by("-id")
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filtering through related models
    filterset_fields = {
        "status": ["exact"],
        "receive_order_at": ["gte", "lte"],
        "customer__name": ["icontains"],
        "mejlis_materials__material_type": ["icontains"],  # reverse relation
    }

    search_fields = ["customer__name", "customer__phone", "mejlis_materials__material_type"]
    ordering_fields = ["id", "receive_order_at", "total_price"]


# ✅ Retrieve one order by ID
class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = "id"


# ✅ Update order
class OrderUpdateView(APIView):
    def put(self, request, id, *args, **kwargs):
        logger.info(f"PUT /orders/{id} - Update order request received")
        order = get_object_or_404(Order, id=id)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    order = serializer.save()
                    pdf_url = generate_order_pdf(order)
                    return Response({
                        "message": "Order updated successfully",
                        "order_id": order.id,
                        "pdf_url": request.build_absolute_uri(pdf_url)
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.exception("Error while updating order")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        logger.warning(f"Validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Delete order
class OrderDeleteView(APIView):
    def delete(self, request, id, *args, **kwargs):
        logger.info(f"DELETE /orders/{id} - Delete order request received")
        order = get_object_or_404(Order, id=id)
        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# ✅ Update order status
class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = "id"

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "Status field is required"}, status=status.HTTP_400_BAD_REQUEST)

        valid_statuses = getattr(Order, "STATUS_CHOICES", [])
        valid_keys = [k for k, _ in valid_statuses]
        if new_status not in valid_keys:
            return Response(
                {"error": f"Invalid status. Valid options are: {valid_keys}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save(update_fields=["status"])
        return Response(
            {"message": f"Order {order.id} status updated to {order.status}"},
            status=status.HTTP_200_OK
        )
