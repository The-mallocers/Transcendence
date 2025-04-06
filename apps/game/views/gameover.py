from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients
from apps.game.models import Game


def get(request):
    client = Clients.get_client_by_request(request)
    game_id = request.GET.get("game", "game_not_found")
    if not client.stats.games.all().filter(id=game_id).exists():
        print("No game related to client, this will never happen by accident but it can, so make a special page for dirty hacker !")
        html_content = html_forbidden_error_page(get_token(request))
        return JsonResponse({
        'error': 'You do not have permission to view this game result',
        'html': html_content,
    }, status=403)
    found_game = Game.objects.get(id=game_id)
    client_player_name = client.profile.username
    message = client_score = opponent_score = opponent = None
    print("found_game is :", found_game)
    print("Its stuff is :", vars(found_game))
    print("Game winner is :", found_game.winner)
    pass
    if found_game.winner.client.id == client.id:
        message = "You won !"
        # client_score = found_game.winner_score
        # opponent_score = found_game.loser_score
        # opponent = found_game.loser
    else:
        message = "You lost !"
        # client_score = found_game.loser_score
        # opponent_score = found_game.winner_score
        # opponent = found_game.winner

    # opponent_player_name = opponent.nickname

    # Delete this line later
    client_player_name = opponent_player_name = message = client_score = opponent_score = None

    html_content = render_to_string("pong/../../templates/apps/pong/gameover.html", {
        "csrf_token": get_token(request),
        "client": client_player_name,
        "opponnent": opponent_player_name,
        "message": message,
        "client_score": client_score,
        "opponent_score": opponent_score
    })
    return JsonResponse({
        'html': html_content,
    })
    
def html_forbidden_error_page(token):
    return render_to_string("pong/../../templates/apps/pong/gameover.html", {
    "csrf_token": token,
    "client": "Secret",
    "opponnent": "Secret",
    "message": "FORBIDDEN",
    "client_score": "42",
    "opponent_score": "42"
})
