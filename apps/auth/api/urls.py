from django.urls import path

from apps.auth.api.views import PasswordUpdateView

urlpatterns = [
    path('password/<str:pk>/', PasswordUpdateView.as_view(), name='password-update'),
]