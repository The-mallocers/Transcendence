import random
from time import sleep

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps import game
from apps.client.models import Clients
from apps.game.models import Game


def get(request):
    game_id = request.GET.get("game", "game_not_found")
    found_game = Game.objects.filter(code=game_id).first()
    message = "Opponent Left"
    # Lets add something cute here to get a random message everytime.
    disconnect_messages = [
        "They were probably scared of you.",
        "A win is a win!",
        "Guess they rage quit.",
        "Disconnected... or disappeared into the shadow realm.",
        "They saw your skills and noped out.",
        "Victory by technicality still counts!",
        "Outplayed... by the Wi-Fi router.",
        "Was it lag... or fear?",
        "RIP opponent — gone but not forgotten.",
        "Another one bites the dust (or the disconnect button).",
        "Their device couldn't handle your greatness.",
        "You win! Network issues: your most reliable teammate.",
        "Maybe they just went to get milk.",
        "Bravely ran away, Sir Opponent.",
    ]
    is_won_tourney = False
    client = Clients.get_client_by_request(request)
    if found_game.tournament and found_game.tournament.winner == client.id:
        disconnect_messages = "Your opponent disconnected, making you the tournament winner !"
        is_won_tourney = True
    is_tourney = False
    if found_game.tournament:
        is_tourney = True

    index = random.randint(0, len(disconnect_messages) - 1) 
    html_content = render_to_string("pong/../../templates/apps/pong/disconnect.html", {
        "csrf_token": get_token(request),
        "message": message,
        "disconnect_message": disconnect_messages[index],
        "is_tourney": is_tourney,
        "is_won_tourney": is_won_tourney,
    })
    return JsonResponse({
        'html': html_content,
    })
