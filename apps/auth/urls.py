from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register_get, name='register'),
    path('login', views.login_get, name='login'),
    # path('', RedirectView.as_view(url='/api/auth/login'))
]