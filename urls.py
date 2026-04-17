from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter

from api.views import JobViewSet
# from api.views import MyProfileView  # кейін қосамыз

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

def home(request):
    return HttpResponse("JobKZ API жұмыс істеп тұр!")

router = DefaultRouter()
router.register(r"jobs", JobViewSet, basename="jobs")

urlpatterns = [
    path("", home),

    path("admin/", admin.site.urls),

    # JWT endpoints
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # API routes
    path("api/", include(router.urls)),

    # Profile routes (кейін)
    # path("api/profile/", MyProfileView.as_view()),
]