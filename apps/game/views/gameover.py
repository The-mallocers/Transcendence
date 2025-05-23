from pickle import TRUE
from time import sleep
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients
from apps.game.models import Game
import random

def get(request):
    client = Clients.get_client_by_request(request)
    game_id = request.GET.get("game", "game_not_found")
    found_game = Game.objects.filter(code=game_id).first()
    client_player_name = client.profile.username
    won_tourney = is_lost_tourney = mmr_change = message = client_score = opponent_score = opponent = None
    if found_game.winner.client.id == client.id:
        message = "You won !"
        client_score = found_game.winner.score
        opponent_score = found_game.loser.score
        opponent = found_game.loser.client.profile.username
        mmr_change = "+" + str(found_game.winner.mmr_change) + " mmr !"
        tourney = found_game.tournament
        if tourney:
            #Loop for a bit to find out if we are the tournament winner.
            for i in range(5):
                tmp_game = Game.objects.filter(code=game_id).first()
                if tmp_game.tournament.winner and tmp_game.tournament.winner.id == client.id:
                    won_tourney = True
                    message = "Tournament Won !"
                    break
                sleep(0.1)
    else:
        message = "You lost !"
        if found_game.tournament:
            message = "Tournament lost"
            is_lost_tourney = True
        client_score = found_game.loser.score
        opponent_score = found_game.winner.score
        opponent = found_game.winner.client.profile.username
        mmr_change = str(found_game.loser.mmr_change) + " mmr"
        if mmr_change == "0 mmr":
            mmr_change = zeroMmrSlander()

    html_content = render_to_string("pong/../../templates/apps/pong/gameover.html", {
        "csrf_token": get_token(request),
        "client": client_player_name,
        "opponnent": opponent,
        "message": message,
        "client_score": client_score,
        "opponent_score": opponent_score,
        "mmr_change": mmr_change,
        "found_game": found_game,
        "is_lost_tourney": is_lost_tourney,
        "won_tourney": won_tourney,
    })
    return JsonResponse({
        'html': html_content,
    })

def zeroMmrSlander() -> str:
    slander = [
        'Cannot go below 0 mmr !',
        "0 + 0 = la tete a toto",
        "0 mmr, 0 problems",
    ]
    index = random.randint(0, len(slander) - 1)
    return slander[index]