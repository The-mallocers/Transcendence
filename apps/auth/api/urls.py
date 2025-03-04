from django.urls import path
from . import views
from apps.auth.api.views import PasswordApiView, LoginApiView, RegisterApiView, LogoutApiView

urlpatterns = [
    path('password/<str:pk>/', PasswordApiView.as_view(), name='password'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('register/', RegisterApiView.as_view(), name='register'),
    path('logout/', LogoutApiView.as_view(), name='logout'),
    path('change_two_fa', views.change_two_fa, name='two_fa'),
    path('2facode', views.post_twofa_code, name='2fa'),
]