from django.http import JsonResponse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

from apps.shared.models import Clients

def get(request):
    client = Clients.get_client_by_request(request)
    username = request.GET.get('username', None)
    
    print(f"Received username: {username}")
    html_content = render_to_string("apps/profile/myinformations.html", {
        "csrf_token": get_token(request),
        "isAdmin": client.rights.is_admin,
        "client" : client,
        }),
    return JsonResponse({
        'html': html_content,
    })