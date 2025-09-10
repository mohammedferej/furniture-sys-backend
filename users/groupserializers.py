from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import  get_user_model

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


from django.contrib.auth.models import Permission
from rest_framework import serializers

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


from rest_framework import serializers
from django.contrib.auth.models import User, Group, Permission

# Assign user to groups
class AssignGroupSerializer(serializers.Serializer):
    groups = serializers.ListField(
        child=serializers.CharField(),  # list of group names
        required=True
    )

# Assign permissions to groups
class AssignGroupPermissionSerializer(serializers.Serializer):
    permissions = serializers.ListField(
        child=serializers.CharField(),  # list of codename strings
        required=True
    )
    def validate_permissions(self, value):
        invalid = []
        for codename in value:
            if not Permission.objects.filter(codename=codename).exists():
                invalid.append(codename)
        if invalid:
            raise serializers.ValidationError(f"Permissions not found: {', '.join(invalid)}")
        return value



class AssignPermissionSerializer(serializers.Serializer):
    permissions = serializers.ListField(
        child=serializers.CharField(),  # expects list of codename strings
        required=True
    )





class AssignPermissionsSerializer(serializers.Serializer):
    permissions = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of permission codenames (e.g., 'can_block_user', 'add_customuser')"
    )

    def validate_permissions(self, value):
        invalid = []
        for codename in value:
            if not Permission.objects.filter(codename=codename).exists():
                invalid.append(codename)
        if invalid:
            raise serializers.ValidationError(f"Permissions not found: {', '.join(invalid)}")
        return value
