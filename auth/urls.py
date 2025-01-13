from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('2fa', views.render_two_fa, name='2fa'),
    path('', RedirectView.as_view(url='/auth/login'))
]