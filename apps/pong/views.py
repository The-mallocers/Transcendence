from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from apps.shared.models import Clients
from apps.game.manager import GameManager


# Create your views here.

def pong(request):
    html_content = render_to_string("pong/pong.html", {"csrf_token": get_token(request)})
    return JsonResponse({
        'html': html_content,
    })

def gamemodes(request):
    html_content = render_to_string("pong/gamemodes.html", {"csrf_token": get_token(request)})
    return JsonResponse({
        'html': html_content,
    })

def matchmaking(request):
    client = Clients.get_client_by_request(request)
    html_content = render_to_string("pong/matchmaking.html", {"csrf_token": get_token(request), "client": client})
    return JsonResponse({
        'html': html_content,
    })

def arena(request):
    client = Clients.get_client_by_request(request)
    html_content = render_to_string("pong/arena.html", {
        "csrf_token": get_token(request),
        "client_id": client
        })
    return JsonResponse({
        'html': html_content,
    })

def gameover(request):
    #Need to add a check where if you havent played the game you are out.*args

    client = Clients.get_client_by_request(request)
    game_id = request.GET.get("game", "game_not_found")
    print(game_id)
    found_game = GameManager.get_game_db(game_id)
    print(found_game)
    client_player_name = client.player.nickname
    print(client_player_name)
    message = client_score = opponent_score = opponent = None
    if found_game.winner.id == client.player.id:
        message = "You won !"
        client_score = found_game.winner_score
        opponent_score = found_game.loser_score
        opponent = found_game.loser
    else:
        message = "You lost !"
        client_score = found_game.loser_score
        opponent_score = found_game.winner_score
        opponent = found_game.winner

    opponent_player_name = opponent.nickname
    
    html_content = render_to_string("pong/gameover.html", {
        "csrf_token": get_token(request),
        "client": client_player_name,
        "opponnent": opponent_player_name,
        "message": message,
        "client_score" : client_score,
        "opponent_score": opponent_score
        })
    return JsonResponse({
        'html': html_content,
    })
