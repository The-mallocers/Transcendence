from django.urls import path

from apps.profile.api.views import ProfileApiView

urlpatterns = [
    path('<str:pk>/', ProfileApiView.as_view(), name='profile-update'),
]
