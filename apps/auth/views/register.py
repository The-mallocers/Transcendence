from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string

from apps.auth.api.views import formulate_json_response
from apps.client.models import Clients


def get(req):
    try:
        client = Clients.get_client_by_request(req)
        if client:
            return formulate_json_response(True, 302, "You are logged in !", "/")
    except Exception as e:
        pass
    html_content = render_to_string("apps/auth/register.html", {"csrf_token": get_token(req)})
    return JsonResponse({
        'html': html_content,
    })
