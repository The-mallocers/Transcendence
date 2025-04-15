from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients


def create_tournament(request):
    client = Clients.get_client_by_request(request)
    html_content = render_to_string("apps/pong/createTournament.html", {"csrf_token": get_token(request), "client": client})
    return JsonResponse({
        'html': html_content,
    })

def join_tournament(request):
    client = Clients.get_client_by_request(request)
    rooms = [
        {
            "name" : "minimeow's room",
            "leaderAvatar" : "/assets/imgs/profile/default.png",
            "players" : 6
        },
        {
            "name" : "huh",
            "leaderAvatar" : "/assets/imgs/profile/default.png",
            "players" : 4
        },
        {
            "name" : "huh2",
            "leaderAvatar" : "/assets/imgs/profile/default.png",
            "players" : 8
        },
        {
            "name" : "huh3",
            "leaderAvatar" : "/assets/imgs/profile/default.png",
            "players" : 7
        }
    ]
    html_content = render_to_string("apps/pong/joinTournament.html", {"csrf_token": get_token(request), "client": client, "rooms": rooms})
    return JsonResponse({
        'html': html_content,
    })