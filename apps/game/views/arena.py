from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients


def get(request):
    client = Clients.get_client_by_request(request)
    html_content = render_to_string("apps/pong/arena.html", {
        "csrf_token": get_token(request),
        "client_id": client
    })
    return JsonResponse({
        'html': html_content,
    })
