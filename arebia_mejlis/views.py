from rest_framework import viewsets, permissions
from .models import ArebiaMejlis
from .serializers import ArebiaMejlisSerializer
from .utils import generate_room_svg
import uuid
from django.core.files.base import ContentFile
from cairosvg import svg2pdf

class ArebiaMejlisViewSet(viewsets.ModelViewSet):
    queryset = ArebiaMejlis.objects.all().order_by("-created_at")
    # print("testing :",ArebiaMejlis.objects.all())
    serializer_class = ArebiaMejlisSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        room_shape = serializer.validated_data.get("room_shape", "U")
        segments = serializer.validated_data.get("segments", {})
        name = serializer.validated_data.get("customer_name")
        phone = serializer.validated_data.get("phone")

        # Generate SVG string
        svg_string = generate_room_svg(room_shape, segments)
        print("*******************************")
        print(name,phone)
        # Save SVG as ContentFile
        svg_filename = f"{name+'_'+phone+'_mejlis'}.svg"
        svg_file = ContentFile(svg_string.encode("utf-8"), name=svg_filename)

        # Convert SVG to PDF bytes
        pdf_bytes = svg2pdf(bytestring=svg_string.encode("utf-8"))
        pdf_filename = f"{name+'_'+phone+'_mejlis'}.pdf"
        pdf_file = ContentFile(pdf_bytes, name=pdf_filename)

        serializer.save(svg_file=svg_file, pdf_file=pdf_file)
