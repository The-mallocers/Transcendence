from django.http import JsonResponse

from apps.shared.models import Clients
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

grafana_id = 0

def get(req):
    csrf_token = get_token(req)
    users = Clients.objects.all()
    html_content = render_to_string("apps/auth/login.html", {
        "users": users, 
        "csrf_token": csrf_token,
        })

    return JsonResponse({
        'html': html_content,
        'users': list(users.values())
    })