from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients


def create_local(request):
    client = Clients.get_client_by_request(request)
    # if status == FULL_TOURNEY:
    #     return formulate_json_response(True, 302, "Redirecting to tournament", "/pong/tournament/tree/")
    # elif status == HALF_TOURNEY:
    #     return formulate_json_response(True, 302, "Redirecting to lobby", "/pong/tournament/")
    html_content = render_to_string("apps/pong/createLocal.html", {"csrf_token": get_token(request), "client": client})
    return JsonResponse({
        'html': html_content,
    })


def localGameover(request) :
    html_content = render_to_string("apps/pong/endGameLocal.html", {
    "csrf_token": get_token(request),
    })
    return JsonResponse({
        'html': html_content,
    })