from rest_framework import serializers
from django.contrib.auth.models import Group, Permission, get_user_model

User = get_user_model()

class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        many=True,
        slug_field="codename",
        queryset=Permission.objects.all()
    )

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]
class AssignGroupSerializer(serializers.Serializer):
    groups = serializers.ListField(
        child=serializers.CharField(),  # expects list of group names
        required=True
    )
