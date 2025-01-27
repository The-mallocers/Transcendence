from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PasswordViewSet

router = DefaultRouter()
router.register(r'password', PasswordViewSet)

urlpatterns = [
    path('', include(router.urls))
]
