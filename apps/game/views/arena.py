from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from config import settings


def get(request):
    arena_picture = settings.MEDIA_URL + "art/arena-wallpaper.jpg"
    html_content = render_to_string("apps/pong/arena.html", {
        "csrf_token": get_token(request),
        "arena_picture": arena_picture,
    })

    return JsonResponse({
        'html': html_content,
    })
