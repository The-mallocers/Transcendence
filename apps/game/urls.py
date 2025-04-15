from django.urls import path

from apps.game import view

urlpatterns = [
    path('gamemodes/', view.gamemodes_get, name='gamemodes'),
    path('matchmaking/', view.matchmaking_get, name='matchmaking'),
    path('arena/', view.arena_get, name='arena'),
    path('', view.pong_get, name='pong'),
    path('gameover/', view.gameover_get, name='gameover'),
    path('disconnect/', view.disconnect_get, name='disconnect'),
]
