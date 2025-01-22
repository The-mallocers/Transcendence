from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('register', views.register_get, name='register'),
    path('login', views.login_get, name='login'),
    path('2fa', views.render_two_fa, name='2fa'),
]