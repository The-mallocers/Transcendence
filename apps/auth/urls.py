from django.urls import path

from apps.auth import view

urlpatterns = [
    path('register', view.register_get, name='register'),
    path('login', view.login_get, name='login'),
    path('2fa', view.twofa_get, name='2fa'),
]
