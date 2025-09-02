from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group,Permission

from users.models import CustomUser


from .serializers import (
    AssignGroupSerializer,
    AssignPermissionSerializer,
    AssignPermissionsSerializer,
    AssignRoleSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    UserListSerializer
)
from .permissions import IsAdmin, IsAdmin

User = get_user_model()

# JWT login
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

# Register user
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

# User profile
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# Update logged-in user's profile
class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# Logout
@api_view(['POST'])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out.'})
    except Exception:
        return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

# User list for admin
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdmin]

# Change password for logged-in users
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"error": "Both old and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

# Reset password by admin
class ResetPasswordView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        username = request.data.get("username")
        new_password = request.data.get("new_password")

        if not username or not new_password:
            return Response({"error": "Username and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            return Response({"message": f"Password for {username} reset successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

# Full CRUD + block/unblock for users
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer

    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def block(self, request, pk=None):
        user = self.get_object()
        user.blocked = True
        user.save()
        return Response({"message": "User blocked"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def unblock(self, request, pk=None):
        user = self.get_object()
        user.blocked = False
        user.save()
        return Response({"message": "User unblocked"}, status=status.HTTP_200_OK)
    action(detail=True, methods=["patch"], url_path="assign-permissions")
    def assign_permissions(self, request, pk=None):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = AssignPermissionsSerializer(data=request.data)
        if serializer.is_valid():
            permissions = serializer.validated_data["permissions"]
            for codename in permissions:
                perm = Permission.objects.get(codename=codename)
                user.user_permissions.add(perm)
            return Response({"message": "Permissions assigned successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], url_path="remove-permissions")
    def remove_permissions(self, request, pk=None):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = AssignPermissionsSerializer(data=request.data)
        if serializer.is_valid():
            permissions = serializer.validated_data["permissions"]
            for codename in permissions:
                perm = Permission.objects.get(codename=codename)
                user.user_permissions.remove(perm)
            return Response({"message": "Permissions removed successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# "Me" endpoint for logged-in user
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

class AssignRoleView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AssignRoleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        role = request.data.get("role")
        if role not in dict(user._meta.get_field("role").choices):
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)
        user.role = role
        user.save()
        return Response({"message": f"Role '{role}' assigned to {user.username}"})
    

class AssignPermissionView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AssignPermissionSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        permissions = request.data.get("permissions", [])
        user.user_permissions.clear()
        for perm_codename in permissions:
            try:
                perm = Permission.objects.get(codename=perm_codename)
                user.user_permissions.add(perm)
            except Permission.DoesNotExist:
                return Response({"error": f"Permission '{perm_codename}' not found"}, status=400)
        return Response({"message": f"Permissions updated for {user.username}"})


class AssignGroupView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AssignGroupSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        groups = request.data.get("groups", [])
        user.groups.clear()
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
        return Response({"message": f"Groups updated for {user.username}"})

    