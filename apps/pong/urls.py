from django.urls import path

from . import views

urlpatterns = [
    path('gamemodes/', views.gamemodes, name='gamemodes'),
    path('arena/', views.arena, name='arena'),
    path('', views.pong, name='pong')
]
