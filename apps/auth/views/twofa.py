from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.client.models import Clients


def view_two_fa(req):
    email = req.COOKIES.get('email')
    client = Clients.get_client_by_email(email)
    html_content = render_to_string("apps/auth/2fa.html", {
        "csrf_token": get_token(req),
        "client": client,
    })
    return JsonResponse({'html': html_content, })
