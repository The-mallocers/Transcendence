from django.urls import path

from apps.game import views

urlpatterns = [
    path('gamemodes/', views.gamemodes_get, name='gamemodes'),
    path('matchmaking/', views.matchmaking_get, name='matchmaking'),
    path('arena/', views.arena_get, name='arena'),
    path('', views.pong_get, name='pong'),
    path('gameover/', views.gameover_get, name='gameover'),
]
