from django.urls import path

from . import views

urlpatterns = [
    path('', views.account_get, name='account'),
]