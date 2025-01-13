from django.shortcuts import render
from django.urls import path

from error.views import error_404
from . import views

urlpatterns = [
    path('', views.pong, name='pong')
]
