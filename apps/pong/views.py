from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from apps.shared.models import Clients

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
    html_content = render_to_string("pong/arena.html", {"csrf_token": get_token(request)})
    return JsonResponse({
        'html': html_content,
    })
