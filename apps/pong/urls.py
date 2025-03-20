from django.urls import path

from . import views

urlpatterns = [
    path('gamemodes/', views.gamemodes, name='gamemodes'),
    path('matchmaking/', views.matchmaking, name='matchmaking'),
    path('arena/', views.arena, name='arena'),
    path('', views.pong, name='pong'),
    path('gameover/', views.gameover, name='gameover'),
]
