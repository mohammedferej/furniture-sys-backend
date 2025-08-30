from warnings import filters
from django.db import IntegrityError
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth import get_user_model
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from allauth.account.models import EmailConfirmationHMAC, EmailAddress
from django.utils import timezone

from .serializers import (
    UserListSerializer, UserRegistrationSerializer, UserProfileSerializer, 
    UserUpdateSerializer
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
   def post(self, request, *args, **kwargs):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # if hasattr(user, 'email_verified') and not user.email_verified:
    #     return Response({
    #         'error': 'Please verify your email before logging in',
    #         'needs_verification': True
    #     }, status=status.HTTP_401_UNAUTHORIZED)

    response = super().post(request, *args, **kwargs)
    if response.status_code == 200:
        user_data = UserProfileSerializer(user).data
        response.data['user'] = user_data
        user.last_login = timezone.now()
        user.save()

    return response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                self.send_verification_email(user)
                return Response({
                    'message': 'Registration successful. Please check your email to verify your account.',
                    'user_id': user.id,
                    'username': user.username
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({
                    'error': 'User with this username or email already exists.',
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user):
        try:
            email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False
            )

            confirmation = EmailConfirmationHMAC(email_address)

            activation_url = '{}/verify-email/{}'.format(
                getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
                confirmation.key
            )

            subject = "Verify your account"
            message = render_to_string('email_verification.html', {
                'user': user,
                'activation_url': activation_url,
                'expiry_days': getattr(settings, 'EMAIL_CONFIRMATION_EXPIRE_DAYS', 1),
            })

            email = EmailMessage(subject, message, to=[user.email])
            email.content_subtype = "html"
            email.send()

        except Exception as e:
            print(f"Failed to send verification email: {e}")


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, key):
        try:
            confirmation = EmailConfirmationHMAC.from_key(key)
            if not confirmation:
                return Response({'error': 'Invalid or expired confirmation key'}, status=status.HTTP_400_BAD_REQUEST)

            email_address = confirmation.email_address

            if email_address.verified:
                return Response({'message': 'Email already verified'}, status=status.HTTP_200_OK)

            confirmed = confirmation.confirm(request)
            if not confirmed:
                return Response({'error': 'Confirmation failed'}, status=status.HTTP_400_BAD_REQUEST)

            user = email_address.user
            if hasattr(user, 'email_verified'):
                user.email_verified = True
                user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Email verified successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if hasattr(user, 'email_verified') and user.email_verified:
                return Response({'message': 'Email already verified'}, status=status.HTTP_200_OK)

            self.send_verification_email(user)
            return Response({'message': 'Verification email sent'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def send_verification_email(self, user):
        try:
            email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False
            )

            confirmation = EmailConfirmationHMAC(email_address)

            activation_url = '{}/verify-email/{}'.format(
                getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
                confirmation.key
            )

            subject = "Verify your account"
            message = render_to_string('email_verification.html', {
                'user': user,
                'activation_url': activation_url,
                'expiry_days': getattr(settings, 'EMAIL_CONFIRMATION_EXPIRE_DAYS', 1),
            })

            email = EmailMessage(subject, message, to=[user.email])
            email.content_subtype = "html"
            email.send()
        except Exception as e:
            print(f"Failed to resend verification email: {e}")


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    print(UserProfileSerializer)

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        if response.status_code == 200:
            response.data = UserProfileSerializer(self.get_object()).data
        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out.'})
    except Exception:
        return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)




class UserListView(generics.ListAPIView):
    # print("search .....")
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username']


    # permission_classes = [permissions.IsAuthenticated]  # or AllowAny if public


# class UserListView(generics.ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserListSerializer

class UpdateUserView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = 'pk'



class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    lookup_field = 'pk'
    # permission_classes = [IsAdminUser] 


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserListSerializer, UserUpdateSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer

    @action(detail=True, methods=['patch'], url_path='block')
    def block_user(self, request, pk=None):
        user = self.get_object()
        # Example: toggle or set 'blocked' attribute, adjust as per your User model
        user.blocked = True
        user.save()
        return Response({'status': 'User blocked'}, status=status.HTTP_200_OK)
