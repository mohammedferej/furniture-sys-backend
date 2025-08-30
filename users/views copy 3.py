from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    UserListSerializer
)
from .permissions import IsAdmin, HasRole

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

class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# Logout
from rest_framework.decorators import api_view

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

# Viewset for user management
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer

    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def block(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'User blocked'})
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

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
    permission_classes = [IsAdminUser]

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


# User CRUD and block/unblock
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def block(self, request, pk=None):
        user = self.get_object()
        user.blocked = True
        user.save()
        return Response({"message": "User blocked"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def unblock(self, request, pk=None):
        user = self.get_object()
        user.blocked = False
        user.save()
        return Response({"message": "User unblocked"}, status=status.HTTP_200_OK)