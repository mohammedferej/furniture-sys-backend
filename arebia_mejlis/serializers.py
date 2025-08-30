from rest_framework import serializers
from .models import ArebiaMejlis

class ArebiaMejlisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArebiaMejlis
        fields = "__all__"
        # print("inside ArebiaMejlisSerializer :",fields)
        read_only_fields = ["svg_file", "pdf_file", "created_at", "updated_at"]
