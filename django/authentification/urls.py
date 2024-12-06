from django.urls import path
from . import views

urlpatterns = [
    path('register/signin', views.register),
    path('login', views.login)
]