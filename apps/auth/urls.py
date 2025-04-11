from django.urls import path

from apps.auth import view

urlpatterns = [
    path('register', view.register_get, name='register'),
    path('login', view.login_get, name='login'),
    path('2fa', view.view_two_fa, name='2fa'),
    path('auth42', view.exchange_42_token, name='auth42'),
    # path('', RedirectView.as_view(url='/api/auth/login'))
]
