from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string


def get(req):
    html_content = render_to_string("apps/auth/register.html", {"csrf_token": get_token(req)})
    return JsonResponse({
        'html': html_content,
    })
