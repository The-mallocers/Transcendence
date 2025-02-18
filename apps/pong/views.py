from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

# Create your views here.

def pong(request):
    html_content = render_to_string("pong/pong.html", {"csrf_token": get_token(request)})
    return JsonResponse({
        'html': html_content,
    })
