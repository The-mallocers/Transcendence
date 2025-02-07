from django.urls import path

from apps.auth.api.views import PasswordApiView, LoginApiView, RegisterApiView

urlpatterns = [
    path('password/<str:pk>/', PasswordApiView.as_view(), name='password'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('register/', RegisterApiView.as_view(), name='register')
]