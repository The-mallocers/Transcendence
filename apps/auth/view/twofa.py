
from django.http import JsonResponse

from apps.shared.models import Clients
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

def view_two_fa(req):
    email = req.COOKIES.get('email')
    client = Clients.get_client_by_email(email)
    html_content = render_to_string("apps/auth/2fa.html", {
        "csrf_token": get_token(req),
        "client" : client,
        })
    print(client.twoFa.qrcode.url)
    return JsonResponse({'html': html_content,})