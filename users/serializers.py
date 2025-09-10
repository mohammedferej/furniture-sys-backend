from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from .models import Role

User = get_user_model()



class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'first_name', 'last_name', 'role']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role']


class UserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role']


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


class AssignRoleSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = User
        fields = ["id", "username", "role"]


class AssignPermissionSerializer(serializers.Serializer):
    permissions = serializers.ListField(
        child=serializers.CharField(),  # expects list of codename strings
        required=True
    )


class AssignGroupSerializer(serializers.Serializer):
    groups = serializers.ListField(
        child=serializers.CharField(),  # expects list of group names
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
