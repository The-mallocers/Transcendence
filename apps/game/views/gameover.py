from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from apps.client.models import Clients
from apps.game.models import Game


def get(request):
    # Need to rewrite this to be viable with the new DB

    client = Clients.get_client_by_request(request)
    game_id = request.GET.get("game", "game_not_found")
    found_game = Game.objects.filter(id=game_id).first()
    client_player_name = client.profile.username
    message = client_score = opponent_score = opponent = None
    if found_game.winner.client.id == client.id:
        message = "You won !"
        client_score = found_game.winner.score
        opponent_score = found_game.loser.score
        opponent = found_game.loser.client.profile.username
    else:
        message = "You lost !"
        client_score = found_game.loser.score
        opponent_score = found_game.winner.score
        opponent = found_game.winner.profile.username

    html_content = render_to_string("pong/../../templates/apps/pong/gameover.html", {
        "csrf_token": get_token(request),
        "client": client_player_name,
        "opponnent": opponent,
        "message": message,
        "client_score": client_score,
        "opponent_score": opponent_score
    })
    return JsonResponse({
        'html': html_content,
    })
