from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from users.groupViews import GroupViewSet, PermissionViewSet


from .views import (
     ChangePasswordView, MeView, RegisterView, CustomTokenObtainPairView, ResetPasswordView, UserProfileView,
    UpdateProfileView, logout_view, UserViewSet, UserListView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group') 
router.register(r'permissions', PermissionViewSet, basename='permission')
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('all/', UserListView.as_view(), name='user_list'),  # Admin only
    path("me/", MeView.as_view(), name="me"),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    
   


]

urlpatterns += router.urls
