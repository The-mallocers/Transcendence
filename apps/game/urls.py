from django.urls import path

from apps.game import view

urlpatterns = [
    path('gamemodes/', view.gamemodes_get, name='gamemodes'),
    path('matchmaking/', view.matchmaking_get, name='matchmaking'),
    path('arena/', view.arena_get, name='arena'),
    path('gameover/', view.gameover_get, name='gameover'),
    path('disconnect/', view.disconnect_get, name='disconnect'),
    path('duel/', view.duel_get, name='duel'),
    path('tournament/create/', view.create_tournament_get, name='createTournament'),
    path('tournament/join/', view.join_tournament_get, name='joinTournament'),
    path('tournament/', view.inTournamentRoom, name='inRoom'),
    path('tournament/tree/', view.inTournamentTree, name='tree'),
]
