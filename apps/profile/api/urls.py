from django.urls import path

from apps.profile.api.views import ProfileUpdateView

urlpatterns = [
    path('<str:pk>/', ProfileUpdateView.as_view(), name='profile-update'),
]