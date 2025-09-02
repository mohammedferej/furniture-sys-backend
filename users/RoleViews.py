from rest_framework import viewsets, status,generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Permission
from rest_framework.views import APIView
from users.roleserializers import RoleSerializer
from users.serializers import AssignRoleSerializer
from .models import CustomUser, Role

from .permissions import IsAdmin

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    # Assign permissions to a role
    @action(detail=True, methods=['post'], url_path='assign-permissions')
    def assign_permissions(self, request, pk=None):
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        if not permission_ids:
            return Response({"error": "No permission IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.add(*permissions)
        return Response({"message": f"Permissions assigned to role '{role.name}' successfully"})

    # Remove permissions from a role
    @action(detail=True, methods=['post'], url_path='remove-permissions')
    def remove_permissions(self, request, pk=None):
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        if not permission_ids:
            return Response({"error": "No permission IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.remove(*permissions)
        return Response({"message": f"Permissions removed from role '{role.name}' successfully"})
class AssignRoleToUserView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        """
        Assign a role to a user.
        Expected JSON body: {"role_id": "<role_id>"}
        """
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        role_id = request.data.get("role_id")
        if not role_id:
            return Response({"error": "role_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

        user.role = role
        user.save()
        return Response({"message": f"Role '{role.name}' assigned to user '{user.username}'"}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Remove a role from a user.
        """
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.role = None
        user.save()
        return Response({"message": f"Role removed from user '{user.username}'"}, status=status.HTTP_200_OK)

class AssignRoleView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AssignRoleSerializer
    permission_classes = [IsAdmin]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return full role details
        role_serializer = RoleSerializer(user.role)
        return Response({
            "id": user.id,
            "username": user.username,
            "role": role_serializer.data
        }, status=status.HTTP_200_OK)
