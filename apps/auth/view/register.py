from django.http import JsonResponse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

def get(req):
    html_content = render_to_string("apps/auth/register.html", {"csrf_token": get_token(req)})
    return JsonResponse({
        'html': html_content,
    })
