from django.http import JsonResponse
from django.urls import path

from apps.game.models import GameRoom
from apps.player.models import Player


def test(req):

    p1 = Player(nickname="Player 1", mmr=100)
    p1.save()
    p2 = Player(nickname="Player 2", mmr=300)
    p2.save()
    p3 = Player(nickname="Player 3", mmr=110)
    p3.save()

    game: GameRoom = GameRoom.create_game(p1, False)

    p1.add_to_matchmaking()
    p2.add_to_matchmaking()
    p3.add_to_matchmaking()

    player = game.matchmaking()
    print(f"Opposent: {player}")

    return JsonResponse({"test": "test"}, status=200)

urlpatterns = [
    path('', test, name='test')
]