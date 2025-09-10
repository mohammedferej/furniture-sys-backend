from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from users.models import CustomUser
from .serializers import (
  
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    UserListSerializer,
    
)

from .permissions import IsAdmin

User = get_user_model()

# ----------------- JWT -----------------
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

# ----------------- Register -----------------
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

# ----------------- User profile -----------------
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# ----------------- Logout -----------------
@api_view(['POST'])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out.'})
    except Exception:
        return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

# ----------------- User list -----------------
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdmin]

# ----------------- Password -----------------
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

# ----------------- User CRUD -----------------
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
        user.is_active = False
        user.save()
        return Response({"message": "User blocked"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def unblock(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"message": "User unblocked"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="assign-permissions")
    def assign_permissions(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = AssignPermissionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permissions = serializer.validated_data["permissions"]
        user.user_permissions.clear()
        for codename in permissions:
            perm = Permission.objects.get(codename=codename)
            user.user_permissions.add(perm)
        return Response({"message": "Permissions assigned successfully"})

    @action(detail=True, methods=["patch"], url_path="remove-permissions")
    def remove_permissions(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = AssignPermissionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permissions = serializer.validated_data["permissions"]
        for codename in permissions:
            perm = Permission.objects.get(codename=codename)
            user.user_permissions.remove(perm)
        return Response({"message": "Permissions removed successfully"})

# ----------------- Me -----------------
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

# ----------------- Group endpoints -----------------
class AssignGroupToUserView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = AssignGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        groups = serializer.validated_data['groups']

        user.groups.clear()
        for name in groups:
            group, _ = Group.objects.get_or_create(name=name)
            user.groups.add(group)

        return Response({"detail": f"Groups assigned to user {user.username}"})

class RemoveGroupFromUserView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = AssignGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        groups = serializer.validated_data['groups']

        for name in groups:
            try:
                group = Group.objects.get(name=name)
                user.groups.remove(group)
            except Group.DoesNotExist:
                continue

        return Response({"detail": f"Groups removed from user {user.username}"})

class AssignPermissionToGroupView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, group_name):
        group = get_object_or_404(Group, name=group_name)
        serializer = AssignGroupPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permissions = serializer.validated_data['permissions']

        group.permissions.clear()
        for codename in permissions:
            try:
                perm = Permission.objects.get(codename=codename)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                continue

        return Response({"detail": f"Permissions assigned to group {group.name}"})

class RemovePermissionFromGroupView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, group_name):
        group = get_object_or_404(Group, name=group_name)
        serializer = AssignGroupPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permissions = serializer.validated_data['permissions']

        for codename in permissions:
            try:
                perm = Permission.objects.get(codename=codename)
                group.permissions.remove(perm)
            except Permission.DoesNotExist:
                continue

        return Response({"detail": f"Permissions removed from group {group.name}"})
