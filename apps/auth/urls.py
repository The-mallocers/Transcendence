from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register_get, name='register'),
    path('login', views.login_get, name='login'),
    path('2fa', views.view_two_fa, name='2fa'),
    path('auth42', views.exchange_42_token, name='auth42'),
    # path('', RedirectView.as_view(url='/api/auth/login'))
]