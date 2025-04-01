from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string


def get(request):
    html_content = render_to_string("apps/pong/gamemodes.html", {"csrf_token": get_token(request)})
    return JsonResponse({
        'html': html_content,
    })
