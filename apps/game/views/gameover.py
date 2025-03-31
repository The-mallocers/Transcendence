from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string


def get(request):
    # Need to rewrite this to be viable with the new DB

    # client = Clients.get_client_by_request(request)
    # game_id = request.GET.get("game", "game_not_found")
    # print(game_id)
    # found_game = GameManager.get_game_db(game_id)
    # print(found_game)
    # client_player_name = client.player.nickname
    # print(client_player_name)
    # message = client_score = opponent_score = opponent = None
    # if found_game.winner.id == client.player.id:
    #     message = "You won !"
    #     client_score = found_game.winner_score
    #     opponent_score = found_game.loser_score
    #     opponent = found_game.loser
    # else:
    #     message = "You lost !"
    #     client_score = found_game.loser_score
    #     opponent_score = found_game.winner_score
    #     opponent = found_game.winner

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
