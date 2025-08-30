from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArebiaMejlisViewSet

router = DefaultRouter()
router.register(r"arebiamejlis", ArebiaMejlisViewSet, basename="arebiamejlis")

urlpatterns = [
    path("", include(router.urls)),
]
