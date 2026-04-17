from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import JobViewSet, MyProfileView, NotificationViewSet


router = DefaultRouter()

# Jobs API
router.register(r"jobs", JobViewSet, basename="jobs")

# Notifications API
router.register(r"notifications", NotificationViewSet, basename="notifications")


urlpatterns = [
    # DRF router endpoints
    path("", include(router.urls)),

    # Current user profile
    path("me/", MyProfileView.as_view(), name="my-profile"),
]