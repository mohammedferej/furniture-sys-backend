import logging
from rest_framework import status,generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from order.models import Order

from .serializers import OrderSerializer
from order.utils import generate_order_pdf

logger = logging.getLogger("orders")


class CreateOrderView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info("POST /orders - Create order request received")

        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    order = serializer.save()

                    # Generate PDF
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
    
    # List all orders
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by('-id')
    serializer_class = OrderSerializer


# Retrieve / Update / Delete single order
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """
        Full update of order + nested customer + materials
        """
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        """
        Partial update
        """
        return self.partial_update(request, *args, **kwargs)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    
    
