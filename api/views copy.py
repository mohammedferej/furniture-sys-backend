
from django.forms import ValidationError
from order.utils import generate_order_pdf
from rest_framework.decorators import api_view
from rest_framework.response import Response
from customer.models import Customer
from order.models import Order
from materials.mejlis.models import MejlisMaterial, Segment
from datetime import datetime



@api_view(['POST'])
def create_order(request):
    data = request.data
    try:
        customer_data = data.get('customer')
        order_data = data.get('order')

        if not customer_data or not order_data:
            return Response({'error': 'Invalid data'}, status=400)

        # Parse dates from ISO format
        receive_date = datetime.fromisoformat(order_data['receive_order_at'].replace('Z', '+00:00'))
        completed_date = datetime.fromisoformat(order_data['completed_order_at'].replace('Z', '+00:00')) if order_data['completed_order_at'] else None

        # Create customer
        customer, created = Customer.objects.get_or_create(
            phone=customer_data['phone'],
            defaults={
                'name': customer_data['name'],
                'address': customer_data['address'],
            }
        )

        # Create Order
        order = Order.objects.create(
            customer=customer,
            order_code=order_data['order_code'],
            receive_order_at=receive_date,
            completed_order_at=completed_date,
            total_price=order_data['total_price'],
            remaining_payment=order_data['remaining_payment'],

             # Generate SVG string
        # svg_string = generate_room_svg(material_data['room_shape'], material_data['segments'])

        )

        # Create Material
        material_data = order_data['material_details']
        material = MejlisMaterial.objects.create(
            order=order,
            material_type=material_data['material_type'],
            design_type=material_data['design_type'],
            no_of_mekeda=material_data['no_of_mekeda'],
            no_of_pillow=material_data['no_of_pillow'],
            uplift_or_height=material_data['uplift_or_height'],
            room_size=material_data['room_size'],
            room_shape=material_data['room_shape'],
            price_per_meter=material_data['price_per_meter'],
            app_front=material_data.get('app_front', ''),
            table=material_data.get('table', False)
        )

        # Create Segments
        for side, values in material_data['segments'].items():
            Segment.objects.create(material=material, side_name=side, values=values)

             # Generate and save PDF
        try:
                pdf_path = generate_order_pdf(order)
                return Response({
                    "message": "Order created successfully",
                    "pdf_url": request.build_absolute_uri(order.document.url) if order.document else None
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
                # If PDF generation fails, still return success but with warning
                return Response({
                    "message": "Order created but PDF generation failed",
                    "error": str(e),
                    "order_id": order.id
                }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Order created successfully'})

    except Exception as e:
        return Response({'error': str(e)}, status=500)

