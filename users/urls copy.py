# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, CustomTokenObtainPairView, logout_view,
    UserProfileView, UpdateProfileView, UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', logout_view, name='logout'),

    # Profile
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('me/update/', UpdateProfileView.as_view(), name='update_profile'),

    # User management (router)
    path('', include(router.urls)),

    # If you still want individual update/delete endpoints (optional)
    # path('users/<str:pk>/', UserDetailView.as_view(), ...),
]
